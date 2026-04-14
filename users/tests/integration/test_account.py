from unittest.mock import MagicMock
from httpx import AsyncClient


async def test_full_user_lifecycle(client: AsyncClient, mock_email_service: MagicMock) -> None:
    payload = {
        "username": "test",
        "email": "test@example.com",
        "password": "test12345678",
        "password_confirmation": "test12345678"
    }
    response = await client.post("/api/users", json=payload)
    assert response.status_code == 201

    user_id = response.json()["id"]

    mock_email_service.send_activation_email.assert_called_once()

    activation_code = mock_email_service.send_activation_email.call_args[0][1]

    response = await client.patch(f"/api/users/activation?code={activation_code}")
    assert response.status_code == 200
    assert response.json()["is_active"] is True

    response = await client.get(f"/api/users/?user_id={user_id}")
    assert response.status_code == 200

    user_id = response.json()["id"]

    response = await client.patch(f"/api/users/mfa/enable?user_id={user_id}")
    assert response.status_code == 200

    response = await client.get(f"/api/users/?user_id={user_id}")
    assert response.json()["mfa_secret"] is not None


    response = await client.patch(f"/api/users/mfa/disable?user_id={user_id}")
    assert response.status_code == 200
    assert response.json()["mfa_secret"] is None


    response = await client.delete(f"/api/users?identifier={payload["username"]}")
    assert response.status_code == 204
    response = await client.get(f"/api/users/?user_id={user_id}")
    assert response.status_code == 404


async def test_resend_activation_code(client: AsyncClient, mock_email_service: MagicMock) -> None:
    email = "test@example.com"
    await client.post("/api/users", json={
        "username": "test",
        "email": email,
        "password": "test12345678",
        "password_confirmation": "test12345678"
    })
    mock_email_service.send_activation_email.reset_mock()

    response = await client.post(f"/api/users/activation/code?identifier={email}")
    assert response.status_code == 200

    mock_email_service.send_activation_email.assert_called_once()

async def test_reset_password_flow(client: AsyncClient, mock_email_service: MagicMock) -> None:
    email = "test@example.com"
    await client.post("/api/users", json={
        "username": "test",
        "email": email,
        "password": "test12345678",
        "password_confirmation": "test12345678"
    })
    code = mock_email_service.send_activation_email.call_args[0][1]
    mock_email_service.send_activation_email.reset_mock()

    response = await client.patch(f"/api/users/activation?code={code}")
    assert response.status_code == 200

    response = await client.post(f"/api/users/password/forgot?identifier={email}")
    assert response.status_code == 200

    html_body = mock_email_service.send_email.call_args[0][2]
    token = html_body.split("Reset token: ")[1].split("<")[0]

    response = await client.post(f"/api/users/password/reset", json={"token": token, "new_password": "test1234"})
    assert response.status_code == 200


async def test_validation_error(client: AsyncClient) -> None:
    response = await client.post("/api/users", json={
        "username": "test",
        "email": "test@example.com",
        "password": "bad",
        "password_confirmation": "bad"
    })

    assert response.status_code == 422

async def test_duplicate_user(client: AsyncClient) -> None:
    payload = {
        "username": "test",
        "email": "test@example.com",
        "password": "test12345678",
        "password_confirmation": "test12345678"
    }
    await client.post("/api/users", json=payload)

    response = await client.post(f"/api/users", json=payload)
    assert response.status_code == 409

async def test_bad_endpoint(client: AsyncClient) -> None:
    response = await client.get("/api/user/bad")
    assert response.status_code == 404


