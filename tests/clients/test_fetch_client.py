from typing import TYPE_CHECKING
import pytest
from httpx import AsyncClient

if TYPE_CHECKING:
    from ..conftest import CreatedClientType

pytestmark = pytest.mark.asyncio


async def test_fetch_with_valid_api_key(
    client: AsyncClient, created_client: "CreatedClientType"
) -> None:
    headers = {
        "X-Client-ID": created_client["client_id"],
        "X-Api-Key": created_client["api_key"],
    }

    response = await client.get("/clients/fetch", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    assert response_data["error"] is None
    assert "api_key" in response_data["client"]


async def test_fetch_with_invalid_api_key(
    client: AsyncClient, created_client: "CreatedClientType"
) -> None:
    api_key = created_client["api_key"] + "!"
    headers = {"X-Client-ID": created_client["client_id"], "X-Api-Key": api_key}

    response = await client.get("/clients/fetch", headers=headers)
    assert response.status_code == 401
    response_data = response.json()
    assert response_data["detail"]
