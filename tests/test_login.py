import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import create_hash
from app.schemas import Client


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, session: AsyncSession) -> None:
    password: str = "a_strong_password"
    user_in_db = Client(
        client_id="testuser_example.com",
        full_name="Test User",
        email="test@example.com",
        date_of_birth="2000-01-01",
        gender="Test",
        country="Testland",
        password_hash=create_hash(password),
    )
    session.add(user_in_db)
    await session.commit()

    login_data: dict[str, str] = {"email": "test@example.com", "password": password}
    response = await client.post("/clients/login", json=login_data)

    assert response.status_code == 200
    response_data = response.json()
    assert "api_key" in response_data
    assert response_data["client_id"] == "testuser_example.com"
