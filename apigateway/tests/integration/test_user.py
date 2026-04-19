import respx
from httpx import AsyncClient, Response
from apigateway.core.config import Settings


@respx.mock
async def test_get_user(client: AsyncClient, test_settings: Settings, user_token: str) -> None:
    respx.get(f"{test_settings.USERS_SERVICE_URL}", params={"user_id": "test_user"}).mock(
        return_value=Response(200, json=
        {
            "id": "user_id",
            "username": "test_username",
            "email": "testuser@exmple.com",
            "role": "user",
            "is_active": True,
            "mfa_secret": None
        })
    )

    response = await client.get("/api/user", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200

@respx.mock
async def test_enable_mfa(client: AsyncClient, test_settings: Settings, user_token: str) -> None:
    respx.get(f"{test_settings.USERS_SERVICE_URL}", params={"user_id": "test_user"}).mock(
        return_value=Response(200, json=
        {
            "id": "user_id",
            "username": "test_username",
            "email": "testuser@exmple.com",
            "role": "user",
            "is_active": True,
            "mfa_secret": None
        })
    )

    respx.patch(f"{test_settings.USERS_SERVICE_URL}/mfa/enable", params={"user_id": "user_id"}).mock(
        return_value=Response(200, json={
            "user_id": "user_id",
            "provisioning_uri": "uri",
            "qr_code_base64": "qr"
        })
    )

    response = await client.patch("/api/user/mfa/enable", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200


@respx.mock
async def test_disable_mfa(client: AsyncClient, test_settings: Settings, user_token: str) -> None:
    respx.get(f"{test_settings.USERS_SERVICE_URL}", params={"user_id": "test_user"}).mock(
        return_value=Response(200, json=
        {
            "id": "user_id",
            "username": "test_username",
            "email": "testuser@exmple.com",
            "role": "user",
            "is_active": True,
            "mfa_secret": "SECRET"
        })
    )

    respx.patch(f"{test_settings.USERS_SERVICE_URL}/mfa/disable", params={"user_id": "user_id"}).mock(
        return_value=Response(200, json={
            "id": "user_id",
            "username": "test_username",
            "email": "testuser@exmple.com",
            "role": "user",
            "is_active": True,
            "mfa_secret": None
        })
    )

    response = await client.patch("/api/user/mfa/disable", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200

@respx.mock
async def test_role_mismatch(client: AsyncClient, test_settings: Settings, user_token: str) -> None:
    respx.get(f"{test_settings.USERS_SERVICE_URL}", params={"user_id": "test_user"}).mock(
        return_value=Response(200, json={
            "id": "user_id",
            "username": "test_username",
            "email": "testuser@exmple.com",
            "role": "user",
            "is_active": True,
            "mfa_secret": None
        }
        )
    )
    response = await client.delete("/api/admin/users?identifier=test_user1", headers={"Authorization": f"Bearer {user_token}"})

    assert response.status_code == 403