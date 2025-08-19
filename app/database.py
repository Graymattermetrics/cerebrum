"""Creates and returns the initialised database connection.

Utilises dependency injections to pass the database connection into the app.
"""

from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.schemas import Base

path = Path("/data/db.sqlite")
if not path.exists():
    path.mkdir(parents=True, exist_ok=True)

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:////data/db.sqlite"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, autocommit=False, autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
