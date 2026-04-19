from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException, Request
from jose import jwt
from apigateway.clients.users_client import UsersClient
from apigateway.core.config import Settings
from apigateway.api import dependencies as deps
from apigateway.domain.schemas import UserRead, TokenPayload
import pytest


def test_dependencies_factories_lifecycle(test_settings: Settings) -> None:
    s1 = deps.get_settings()
    s2 = deps.get_settings()

    assert s1 == s2

    httpx_client = deps.get_httpx_client(s1)
    service_request_client = deps.get_service_request_client(httpx_client)
    users_client = deps.get_users_client(service_request_client, s1)

    assert isinstance(users_client, UsersClient)

    assert deps.get_auth_service(users_client, s1).users_client == users_client

async def test_invalid_token_format(test_settings: Settings) -> None:
    with pytest.raises(HTTPException) as exc:
        await deps.get_token_payload("invalid_token", test_settings)
    assert exc.value.status_code == 401

async def test_get_token_payload_user_is_none(test_settings: Settings) -> None:
    token = jwt.encode(claims={}, key=test_settings.JWT_SECRET_KEY, algorithm=test_settings.JWT_ALGORITHM)
    with pytest.raises(HTTPException) as exc:
        await deps.get_token_payload(token, test_settings)
    assert exc.value.status_code == 401

async def test_get_current_user_inactive(test_settings: Settings) -> None:
    mock_user_client = MagicMock()
    mock_user_client.get_user_by_id = AsyncMock(return_value=UserRead(
        id="user_id",
        username="username",
        email="test@email.example.com",
        role="user",
        is_active=False
    ))

    with pytest.raises(HTTPException, match=f"User inactive") as exc:
        await deps.get_current_active_user(TokenPayload(sub="user_id", type="access"), mock_user_client)

    assert exc.value.status_code == 400

async def test_get_current_user_validation_error(test_settings: Settings) -> None:
    mock_user_client = MagicMock()
    mock_user_client.get_user_by_id = AsyncMock(side_effect=Exception())

    with pytest.raises(HTTPException) as exc:
        await deps.get_current_active_user(TokenPayload(sub="user_id", type="access"), mock_user_client)
    assert exc.value.status_code == 503

def test_get_refresh_token_if_not_token(test_settings: Settings) -> None:
    req = Request({"type": "http", "headers": []})
    with pytest.raises(HTTPException) as exc:
         deps.get_refresh_token(req, test_settings)
    assert exc.value.status_code == 401

def test_get_refresh_token_invalid(test_settings: Settings) -> None:
    req = Request({"type": "http", "headers": [(b"cookie", b"refresh_token=bad_token")]})
    with pytest.raises(HTTPException) as exc:
         deps.get_refresh_token(req, test_settings)
    assert exc.value.status_code == 401

def test_get_refresh_token_wrong_type(test_settings: Settings) -> None:
    payload = {"sub": "user_id", "type": "access"}
    token = jwt.encode(claims=payload, key=test_settings.JWT_SECRET_KEY, algorithm=test_settings.JWT_ALGORITHM)
    req = Request({"type": "http", "headers": [(b"cookie", f"refresh_token={token}".encode())]})
    with pytest.raises(HTTPException) as exc:
        deps.get_refresh_token(req, test_settings)
    assert exc.value.status_code == 401






