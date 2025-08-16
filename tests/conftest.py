"""Sets up the fixtures for the tests."""

import datetime
from typing import AsyncGenerator, TypedDict

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from pytest import FixtureRequest, Parser
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.main import app
from app.utils import create_hash
from app.schemas import Base, Client

TEST_SQLALCHEMY_DATABASE_URL: str = "sqlite+aiosqlite:///./test.sqlite"

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


class CreatedClientType(TypedDict):
    client_id: str
    api_key: str
    email: str
    password: str
    password_hash: str


@pytest_asyncio.fixture(scope="function")
async def created_client(
    session: AsyncSession,
) -> AsyncGenerator[CreatedClientType, None]:
    """
    Fixture to create a client and a plaintext API key in the database.
    Returns a dictionary with client details and the key.
    """
    password = "ABC"
    password_hash = create_hash(password)

    test_client = Client(
        client_id="test-auth-123",
        full_name="Test User",
        email="test.auth@example.com",
        date_of_birth=datetime.date(1974, 1, 1),
        gender="Test",
        country="Testland",
        password_hash=password_hash,
    )

    session.add(test_client)
    await session.commit()
    await session.refresh(test_client)

    client_data = CreatedClientType(
        client_id=test_client.client_id,
        api_key=test_client.api_key,
        email=test_client.email,
        password=password,
        password_hash=test_client.password_hash,
    )

    yield client_data

    await session.delete(test_client)
    await session.commit()
