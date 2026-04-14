from unittest.mock import patch
from httpx import AsyncClient


async def test_healthcheck(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_unhandled_exception_handler(client: AsyncClient) -> None:
    with patch("users.services.account_service.AccountService.get_user_by_id", side_effect=Exception("Critical")):
        response = await client.get("/api/users/?user_id=test_id")
        assert response.status_code == 500
        assert response.json()["error"] == "internal server error"
