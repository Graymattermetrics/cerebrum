import pytest_asyncio
from typing import AsyncGenerator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.database import get_db
from app.schemas import Base

TEST_SQLALCHEMY_DATABASE_URL: str = "sqlite+aiosqlite:///./test.sql"

engine = create_async_engine(TEST_SQLALCHEMY_DATABASE_URL)

TestingAsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, autocommit=False, autoflush=False
)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingAsyncSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="session")
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingAsyncSessionLocal() as db_session:
        yield db_session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="module")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client