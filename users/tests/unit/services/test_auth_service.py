from unittest.mock import MagicMock, AsyncMock, patch

import pyotp

from users.core.exceptions import NotFoundException, ValidationException
from users.domain.models import User
from users.domain.schemas import UserLogin, MfaVerify
from users.services.auth_service import AuthService
import pytest


@pytest.fixture
def mock_repo() -> MagicMock:
    return MagicMock()

@pytest.fixture
def auth_service(mock_repo: MagicMock) -> AuthService:
    return AuthService(mock_repo)

async def test_verify_credentials_success(auth_service: AuthService, mock_repo: MagicMock) -> None:
    mock_user = MagicMock(spec=User)
    mock_repo.get_active_by_identifier = AsyncMock(return_value=mock_user)

    with patch("users.services.auth_service.verify_password", return_value=True):
        result = await auth_service.verify_credentials(UserLogin(identifier="testuser", password="password1234"))

    assert result == mock_user

async def test_verify_mfa_user_not_found(auth_service: AuthService, mock_repo: MagicMock) -> None:
    mock_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="User not found"):
        await auth_service.verify_user_mfa(MfaVerify(user_id="user_id", code="123456"))


async def test_verify_mfa_user_invalid_code(auth_service: AuthService, mock_repo: MagicMock) -> None:
    mock_user = MagicMock(spec=User)
    mock_user.mfa_secret = "JBSWY3DPEHPK3PXP"
    mock_repo.get_by_id = AsyncMock(return_value=mock_user)

    with patch.object(AuthService, "_verify_mfa_code", return_value=False):
        with pytest.raises(ValidationException, match="Invalid MFA code"):
            await auth_service.verify_user_mfa(MfaVerify(user_id="user_id", code="123456"))





