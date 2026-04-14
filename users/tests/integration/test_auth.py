import urllib

import pyotp
from httpx import AsyncClient


async def test_auth_mfa_success(client: AsyncClient) -> None:
    payload = {
        "username": "test",
        "email": "test@example.com",
        "password": "test12345678",
        "password_confirmation": "test12345678"
    }
    resp = await client.post(f"/api/users", json=payload)

    user_id = resp.json()["id"]

    resp = await client.patch(f"/api/users/mfa/enable?user_id={user_id}")

    secret_url = resp.json()["provisioning_uri"]

    parsed = urllib.parse.urlparse(secret_url)
    secret = urllib.parse.parse_qs(parsed.query)["secret"][0]

    totp = pyotp.TOTP(secret)
    code = totp.now()

    response = await client.post(f"/api/users/mfa/verify", json={"user_id": user_id, "code": code})
    assert response.status_code == 200
    assert response.json()["username"] == "test"


async def test_login_invalid_credentials(client: AsyncClient) -> None:
    response = await client.post(f"/api/users/auth", json={
        "identifier": "test",
        "password": "badpassword"
    })
    assert response.status_code == 400
    assert response.json()["error"] == "validation error"

async def test_verify_mfa_not_enabled(client: AsyncClient) -> None:
    payload = {
        "username": "test",
        "email": "test@example.com",
        "password": "test12345678",
        "password_confirmation": "test12345678"
    }
    response = await client.post(f"/api/users", json=payload)

    user_id = response.json()["id"]

    response = await client.post(f"/api/users/mfa/verify", json={"user_id": user_id, "code": "123456"})
    assert response.status_code == 400

    assert "User has no mfa secret" in response.json()["detail"]

