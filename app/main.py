"""Handles API endpoints.

Implements middleware on the app.
"""

import hashlib
import secrets

import fastapi
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import ClientCreate, LoginBody, LoginResponse
from app.schemas import Client

app = fastapi.FastAPI()
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
async def login(body: LoginBody) -> LoginResponse: ...  # type: ignore


@app.post("/clients/signup", status_code=201)
async def client_signup(
    client: ClientCreate, db: AsyncSession = Depends(get_db)
) -> None:
    password_hash = create_hash(client.password)
    client_id = secrets.token_urlsafe(64)[:10]

    db_client = Client(
        client_id=client_id,
        email=client.email,
        password_hash=password_hash,
        **client.model_dump(exclude={"password", "email"}),
    )
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
