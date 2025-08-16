"""Implements dependency injections for API keys."""

from fastapi import Depends, Header, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import Client


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    return api_key == hashed_key


async def get_client_id_from_api_key(
    x_api_key: str = Header(),
    x_client_id: str = Header(),
    db: AsyncSession = Depends(get_db),
) -> str:
    """
    Dependency function to authenticate requests by looking up the client
    and verifying the API key in the database.
    """
    if not x_api_key or not x_client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key or X-Client-ID header",
        )

    query = select(Client).where(Client.client_id == x_client_id)
    result = await db.execute(query)
    client = result.scalars().first()
    if not client or not verify_api_key(x_api_key, client.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Client ID or API Key",
        )

    return client.client_id
