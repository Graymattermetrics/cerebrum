"""Handles API endpoints.

Implements middleware on the app.
"""

from contextlib import asynccontextmanager
import hashlib
import secrets
import uuid

import fastapi
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import create_db_and_tables, get_db
from app.models import Client_Create_Model_, LoginBody_Model_, LoginResponse_Model_
from app.schemas import Client


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


def create_hash(x: str) -> str:
    return hashlib.sha256(x.encode()).hexdigest()


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

    return LoginResponse_Model_(
        success=True,
        client=client,  # type: ignore
        error=None,
    )


@app.post("/clients/signup", status_code=201)
async def client_signup(
    client: Client_Create_Model_, db: AsyncSession = Depends(get_db)
) -> LoginResponse_Model_:
    query = select(Client).where(Client.email == client.email.lower().strip())
    result = await db.execute(query)
    existing_client = result.scalar_one_or_none()

    if existing_client:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

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

    return LoginResponse_Model_(
        success=True,
        error=None,
        client=db_client,  # type: ignore
    )
