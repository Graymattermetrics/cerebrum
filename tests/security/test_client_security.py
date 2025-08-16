from typing import TYPE_CHECKING
import pytest
from httpx import AsyncClient


if TYPE_CHECKING:
    from ..conftest import CreatedClientType

pytestmark = pytest.mark.asyncio


async def test_login_with_valid_password(
    client: AsyncClient, created_client: "CreatedClientType"
) -> None:
    login_data = {
        "email": created_client["email"],
        "password": created_client["password"],
    }

    response = await client.post("/clients/login", json=login_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    assert response_data["error"] is None
    assert "api_key" in response_data["client"]


async def test_login_with_invalid_password_incorrect(
    client: AsyncClient, created_client: "CreatedClientType"
) -> None:
    password = created_client["password"] + "!"
    login_data = {"email": created_client["email"], "password": password}

    response = await client.post("/clients/login", json=login_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is False
    assert response_data["error"]
    assert response_data["client"] is None


async def test_login_with_invalid_password_case_sensitive(
    client: AsyncClient, created_client: "CreatedClientType"
) -> None:
    swap_case_password = "".join(
        c.lower() if c.isupper() else c.upper() for c in created_client["password"]
    )
    login_data = {"email": created_client["email"], "password": swap_case_password}

    response = await client.post("/clients/login", json=login_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is False
    assert response_data["error"]
    assert response_data["client"] is None
