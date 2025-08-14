"""Sets up the fixtures for the tests."""

from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from pytest import FixtureRequest, Parser
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.main import app
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


def pytest_addoption(parser: Parser):
    parser.addoption(
        "--keep",
        action="store_true",
        default=False,
        help="Keep the test database after the run.",
    )


@pytest_asyncio.fixture(scope="session")
async def session(request: FixtureRequest) -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestingAsyncSessionLocal() as db_session:
        yield db_session

    if not request.config.getoption("--keep"):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="module")
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
