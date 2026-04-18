import respx
from httpx import AsyncClient, Response
from apigateway.core.config import Settings


@respx.mock
async def test_delete_user(client: AsyncClient, test_settings: Settings, admin_token: str) -> None:
    respx.get(f"{test_settings.USERS_SERVICE_URL}", params={"user_id": "test_admin"}).mock(
        return_value=Response(status_code=200, json={
            "id": "admin_id",
            "username": "test_admin",
            "email": "testadmin@exmple.com",
            "role": "admin",
            "is_active": True,
            "mfa_secret": None
        })
    )

    respx.delete(f"{test_settings.USERS_SERVICE_URL}", params={"identifier": "test_user"}).mock(
        return_value=Response(status_code=204)
    )

    params = {"identifier": "test_user"}

    response = await client.delete(
        "/api/admin/users",
        params=params,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204