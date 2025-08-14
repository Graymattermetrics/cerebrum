from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

SQLALCHEMY_DATABASE_URL: str = "sqlite+aiosqlite:///./sql_app.db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, autocommit=False, autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session