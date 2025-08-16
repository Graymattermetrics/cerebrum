"""Handles API endpoints.

Implements middleware on the app.
"""

from contextlib import asynccontextmanager
import secrets
import uuid

import fastapi
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import create_db_and_tables, get_db
from app.models import (
    Client_Create_Model_,
    LoginBody_Model_,
    LoginResponse_Model_,
    CogspeedTestResult_Model_,
)
from app.schemas import Client, CogspeedTestResult, CogspeedTestRound
from app.security import get_client_id_from_api_key
from app.utils import create_hash


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()

    yield


app = fastapi.FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/")
async def get_root():
    return "Hello"


@app.post("/clients/login")
async def login(
    body: LoginBody_Model_, db: AsyncSession = Depends(get_db)
) -> LoginResponse_Model_:
    hash_password = create_hash(body.password)
    email_address = body.email.lower().strip()

    query = select(Client).where(
        Client.email == email_address and Client.password_hash == hash_password
    )
    result = await db.execute(query)
    client = result.scalar_one_or_none()

    if client is None:
        return LoginResponse_Model_(
            success=False, error="Client does not exist", client=None
        )

    return LoginResponse_Model_(success=True, client=client, error=None)  # type: ignore


@app.post("/clients/signup", status_code=status.HTTP_201_CREATED)
async def client_signup(
    client: Client_Create_Model_, db: AsyncSession = Depends(get_db)
) -> LoginResponse_Model_:
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

    return LoginResponse_Model_(success=True, error=None, client=db_client)  # type: ignore


@app.post("/clients/cogspeed/tests", status_code=status.HTTP_201_CREATED)
async def post_cogspeed_test(
    test: CogspeedTestResult_Model_,
    db: AsyncSession = Depends(get_db),
    client_id: str = Depends(get_client_id_from_api_key),
) -> int:
    if client_id != test.client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The client ID in the header ('{client_id}') does not match the client ID in the body ('{test.client_id}').",
        )

    metadata = {"client_id": test.client_id, "test_id": test.id}
    rounds = [metadata | r.model_dump() for r in test.rounds]

    db_cogspeed_test_result = CogspeedTestResult(
        rounds=[CogspeedTestRound(**r) for r in rounds],
        **test.model_dump(exclude={"rounds"}),
    )
    db.add(db_cogspeed_test_result)
    await db.commit()
    await db.refresh(db_cogspeed_test_result)

    return status.HTTP_201_CREATED
