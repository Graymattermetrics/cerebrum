import secrets
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import ClientCreateModel, LoginBodyModel, LoginResponseModel
from app.schemas import Client
from app.security import get_client_id_from_api_key
from app.utils import create_hash

router = APIRouter()


@router.post("/clients/login")
async def login(
    body: LoginBodyModel, db: AsyncSession = Depends(get_db)
) -> LoginResponseModel:
    hash_password = create_hash(body.password)
    email_address = body.email.lower().strip()

    query = select(Client).where(
        Client.email == email_address, Client.password_hash == hash_password
    )
    result = await db.execute(query)

    client = result.scalar_one_or_none()

    if client is None:
        return LoginResponseModel(
            success=False, error="Client does not exist", client=None
        )

    return LoginResponseModel(success=True, client=client, error=None)  # type: ignore


@router.post("/clients/signup", status_code=status.HTTP_201_CREATED)
async def client_signup(
    client: ClientCreateModel, db: AsyncSession = Depends(get_db)
) -> LoginResponseModel:
    query = select(Client).where(Client.email == client.email.lower().strip())
    result = await db.execute(query)
    existing_client = result.scalar_one_or_none()

    if existing_client:
        raise HTTPException(status_code=409, detail="Email already registered")

    password_hash = create_hash(client.password)
    client_id = secrets.token_urlsafe(64)[:10]
    api_key = str(uuid.uuid4())

    db_client = Client(
        client_id=client_id,
        email=client.email,
        password_hash=password_hash,
        api_key=api_key,
        **client.model_dump(exclude={"password", "email"}),
    )
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)

    return LoginResponseModel(success=True, error=None, client=db_client)  # type: ignore


@router.get("/clients/fetch", status_code=status.HTTP_200_OK)
async def get_client(
    x_api_key: str = Header(),
    client_id: str = Depends(get_client_id_from_api_key),
    db: AsyncSession = Depends(get_db),
) -> LoginResponseModel:
    query = select(Client).where(
        Client.client_id == client_id, Client.api_key == x_api_key
    )
    result = await db.execute(query)
    client = result.scalar_one_or_none()
    if not client:
        return LoginResponseModel(success=False, error="Client not found", client=None)

    return LoginResponseModel(success=True, error=None, client=client)  # type: ignore
