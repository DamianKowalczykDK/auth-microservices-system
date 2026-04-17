import respx
from httpx import AsyncClient, Response
from apigateway.core.config import Settings


@respx.mock
async def test_create_user(client: AsyncClient ,test_settings: Settings) -> None:
    respx.post(f"{test_settings.USERS_SERVICE_URL}").mock(
        return_value=Response(status_code=201, json={
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
        "email": "testuser@exmple.com",
        "password": "password123",
        "password_confirmation": "password123"
    }

    response = await client.post("/api/accounts", json=payload)
    assert response.status_code == 201

@respx.mock
async def test_activate_user(client: AsyncClient ,test_settings: Settings) -> None:
    respx.patch(f"{test_settings.USERS_SERVICE_URL}/activation").mock(
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
    query = {
        "code": "code1234"
    }

    response = await client.patch("/api/accounts/activation", params=query)
    assert response.status_code == 200

@respx.mock
async def test_resend_activate_code(client: AsyncClient, test_settings: Settings) -> None:
    respx.post(f"{test_settings.USERS_SERVICE_URL}/activation/code").mock(
        return_value=Response(status_code=200, json={
            "message": "user_id's activation code has been sent."
        }
        )
    )
    query = {
        "identifier": "user_id"
    }

    response = await client.post("/api/accounts/activation/code", params=query)
    assert response.status_code == 200

@respx.mock
async def test_forgot_password(client: AsyncClient, test_settings: Settings) -> None:
    respx.post(f"{test_settings.USERS_SERVICE_URL}/password/forgot").mock(
        return_value=Response(status_code=200, json={
            "message": "ok"
        }
        )
    )
    query = {
        "identifier": "user_id"
    }

    response = await client.post("/api/accounts/password/forgot", params=query)
    assert response.status_code == 200

@respx.mock
async def test_reset_password(client: AsyncClient, test_settings: Settings) -> None:
    respx.post(f"{test_settings.USERS_SERVICE_URL}/password/reset").mock(
        return_value=Response(status_code=200, json={
            "message": "ok"
        }
        )
    )
    payload = {
    "token": "token",
    "new_password": "password12345678"
}

    response = await client.post("/api/accounts/password/reset", json=payload)
    assert response.status_code == 200