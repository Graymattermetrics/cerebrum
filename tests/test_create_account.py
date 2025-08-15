"""Implements tests for the /clients/signup endpoint."""

import datetime
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import create_hash
from app.schemas import Client

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


async def test_client_signup_success(
    client: AsyncClient, session: AsyncSession
) -> None:
    """
    Tests successful creation of a new client account.
    """
    client_data = {
        "full_name": "Test User",
        "email": "test.user.signup.success@example.com",
        "date_of_birth": "1995-06-15",
        "gender": "Female",
        "country": "Testland",
        "password": "a_very_secure_password_123",
    }

    response = await client.post("/clients/signup", json=client_data)

    assert response.status_code == 201

    query = select(Client).where(Client.email == client_data["email"])
    result = await session.execute(query)
    db_client = result.scalar_one_or_none()

    assert db_client is not None
    assert db_client.email == client_data["email"]
    assert db_client.full_name == client_data["full_name"]
    assert db_client.country == "Testland"

    # Verify the password was hashed and not stored in plain text
    expected_hash = create_hash(client_data["password"])
    assert db_client.password_hash == expected_hash
    assert db_client.password_hash != client_data["password"]


async def test_client_signup_duplicate_email(
    client: AsyncClient, session: AsyncSession
) -> None:
    """
    Tests that creating a client with a pre-existing email fails.
    """
    initial_email: str = "duplicate.user@example.com"
    initial_user = Client(
        client_id="initial_user_1",
        full_name="Initial User",
        email=initial_email,
        date_of_birth=datetime.date(1974, 1, 1),
        gender="Male",
        country="Firstland",
        password_hash=create_hash("initial_password"),
    )
    session.add(initial_user)
    await session.commit()

    duplicate_client_data = {
        "full_name": "Duplicate User",
        "email": initial_email,
        "date_of_birth": "2002-02-20",
        "gender": "Other",
        "country": "Secondland",
        "password": "another_password",
    }

    response = await client.post("/clients/signup", json=duplicate_client_data)

    assert response.status_code == 409
    response_json = response.json()
    assert "detail" in response_json
    assert response_json["detail"] == "Email already registered"
