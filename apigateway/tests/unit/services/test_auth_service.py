from unittest.mock import MagicMock, AsyncMock

from fastapi import HTTPException

from apigateway.domain.schemas import UserRead, TokenPayload
from apigateway.services.auth_service import AuthService
import pytest


async def test_refresh_token_user_is_inactive() -> None:
    mock_user_client = MagicMock()
    mock_user_client.get_user_by_id = AsyncMock(return_value=UserRead(
        id="user_id",
        username="username",
        email="test@email.example.com",
        role= "user",
        is_active=False
    ))
    service = AuthService(mock_user_client, MagicMock())
    token = TokenPayload(sub="user_id", type="refresh")

    with pytest.raises(HTTPException, match="User is inactive") as exc:
         await service.refresh_token(token)

    assert exc.value.status_code == 400

