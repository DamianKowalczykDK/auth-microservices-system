import respx
from httpx import AsyncClient, Response
from apigateway.core.config import Settings

@respx.mock
async def test_login_success(client: AsyncClient, test_settings: Settings) -> None:
    respx.post(f"{test_settings.USERS_SERVICE_URL}").mock(
        return_value=Response(status_code=200, json={
            "id": "user_id",
            "username": "test_username",
            "email": "testuser@exmple.com",
            "role": "user",
            "is_active": True,
            "mfa_secret": None
            }
        )
    )

    payload = {
        "username": "test_username",
        "password": "pass1234"
    }
    response = await client.post("/api/auth", data=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.headers.get("set-cookie", "")

@respx.mock
async def test_login_inactive(client: AsyncClient, test_settings: Settings) -> None:
    respx.post(f"{test_settings.USERS_SERVICE_URL}/auth").mock(
        return_value=Response(status_code=200, json={
            "id": "user_id",
            "username": "test_username",
            "email": "testuser@exmple.com",
            "role": "user",
            "is_active": False,
            "mfa_secret": None
            }
        )
    )

    payload = {
        "username": "test_username",
        "password": "pass1234"
    }
    response = await client.post("/api/auth", data=payload)
    assert response.status_code == 400

@respx.mock
async def test_login_mfa_required(client: AsyncClient, test_settings: Settings) -> None:
    respx.post(f"{test_settings.USERS_SERVICE_URL}/auth").mock(
        return_value=Response(status_code=200, json={
            "id": "user_id",
            "username": "test_username",
            "email": "testuser@exmple.com",
            "role": "user",
            "is_active": True,
            "mfa_secret": "SECRET"
            }
        )
    )

    payload = {
        "username": "test_username",
        "password": "pass1234"
    }
    response = await client.post("/api/auth", data=payload)
    assert response.status_code == 200
    assert response.json()["mfa_required"] is True

@respx.mock
async def test_verify_mfa(client: AsyncClient, test_settings: Settings) -> None:
    respx.post(f"{test_settings.USERS_SERVICE_URL}/mfa/verify").mock(
        return_value=Response(status_code=200, json={
            "id": "user_id",
            "username": "test_username",
            "email": "testuser@exmple.com",
            "role": "user",
            "is_active": True,
            "mfa_secret": "Secret"
            })
    )

    payload = {
        "user_id": "user_id",
        "code": "123456"
    }

    response = await client.post("/api/auth/mfa", data=payload)
    assert response.status_code == 200

@respx.mock
async def test_refresh_token(client: AsyncClient, test_settings: Settings, refresh_token: str) -> None:
    respx.get(f"{test_settings.USERS_SERVICE_URL}", params={"user_id": "test_user"}).mock(
        return_value=Response(status_code=200, json={
            "id": "u1",
            "username": "test_username",
            "email": "testuser@exmple.com",
            "role": "user",
            "is_active": True,
            "mfa_secret": None
            })
    )

    client.cookies.set("refresh_token", refresh_token)
    response = await client.post("/api/auth/refresh")
    assert response.status_code == 200
    assert "access_token" in response.json()

@respx.mock
async def test_logout(client: AsyncClient, test_settings: Settings, user_token: str) -> None:
    respx.get(f"{test_settings.USERS_SERVICE_URL}", params={"user_id": "test_user"}).mock(
        return_value=Response(status_code=200, json={
            "id": "user_id",
            "username": "test_username",
            "email": "testuser@exmple.com",
            "role": "user",
            "is_active": True,
            "mfa_secret": None
        })
    )

    client.cookies.set("refresh_token", "")
    response = await client.post("/api/auth/logout", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert "access_token" not in response.json()