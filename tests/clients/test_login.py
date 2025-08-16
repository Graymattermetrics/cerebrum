import datetime
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils import create_hash
from app.schemas import Client

pytestmark = pytest.mark.asyncio


async def test_login_success(client: AsyncClient, session: AsyncSession) -> None:
    password: str = "a_strong_password"
    user_in_db = Client(
        client_id="abcdefghij",
        full_name="Test User",
        email="test.user.login@example.com",
        date_of_birth=datetime.date(1974, 1, 1),
        gender="Test",
        country="Testland",
        password_hash=create_hash(password),
    )
    session.add(user_in_db)
    await session.commit()

    login_data: dict[str, str] = {
        "email": "test.user.login@example.com",
        "password": password,
    }
    response = await client.post("/clients/login", json=login_data)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    assert response_data["error"] is None
    assert "api_key" in response_data["client"]
    assert (c := response_data["client"]["client_id"]) and len(c) == 10


async def test_login_fail(client: AsyncClient, session: AsyncSession) -> None:
    password: str = "a_strong_password"
    user_in_db = Client(
        client_id="testuser_example.com",
        full_name="Test User",
        email="test.user.does.exist@example.com",
        date_of_birth=datetime.date(1974, 1, 1),
        gender="Test",
        country="Testland",
        password_hash=create_hash(password),
    )
    session.add(user_in_db)
    await session.commit()

    login_data: dict[str, str] = {
        "email": "test.user.does.not.exist@example.com",
        "password": password,
    }
    response = await client.post("/clients/login", json=login_data)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is False
    assert response_data["error"]
    assert response_data["client"] is None
