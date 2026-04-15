import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone

from users.core.exceptions import ValidationException, ConflictException, NotFoundException
from users.domain.models import User
from users.services.account_service import AccountService


@pytest.fixture
def mock_repo() -> MagicMock:
    return MagicMock()

@pytest.fixture
def mock_email() -> MagicMock:
    return MagicMock()

@pytest.fixture
def mock_settings() -> MagicMock:
    settings = MagicMock()
    settings.USER_ACTIVATION_EXPIRATION_MINUTES = 10
    settings.RESET_PASSWORD_EXPIRATION_MINUTES = 10
    return settings

@pytest.fixture
def account_service(
        mock_repo: MagicMock,
        mock_email: MagicMock,
        mock_settings: MagicMock
) -> AccountService:
    return AccountService(mock_repo, mock_email, mock_settings)


async def test_activate_user_expired_code(
        account_service: AccountService,
        mock_repo: MagicMock,
) -> None:
    expired_date = datetime.now(timezone.utc) - timedelta(minutes=60)
    mock_user = MagicMock(spec=User)
    mock_user.is_active = False
    mock_user.activation_created_at = expired_date
    mock_repo.get_by_activation_code = AsyncMock(return_value=mock_user)

    with pytest.raises(ValidationException, match="Activation code expired"):
        await account_service.activate_user("old-code")

async def test_activate_user_invalid_code(
        account_service: AccountService,
        mock_repo: MagicMock,
) -> None:
    mock_user = MagicMock(spec=User)
    mock_user.is_active = False
    mock_repo.get_by_activation_code = AsyncMock(return_value=False)

    with pytest.raises(NotFoundException, match="Invalid activation code"):
        await account_service.activate_user("bad-code")

async def test_create_user_if_username_exists(
        account_service: AccountService,
        mock_repo: MagicMock
) -> None:
    bg_task = MagicMock()
    mock_user = MagicMock(spec=User)
    mock_repo.get_by_username = AsyncMock(return_value=mock_user)
    mock_repo.get_by_email = AsyncMock(return_value=False)

    with pytest.raises(ConflictException, match="Username already exists"):
        await account_service.create_user(mock_user, bg_task)

async def test_disable_mfa_no_secret(
        account_service: AccountService,
        mock_repo: MagicMock
) -> None:
    account_service.repository = mock_repo
    mock_user = MagicMock(spec=User)
    mock_user.mfa_secret = None
    mock_repo.get_by_id = AsyncMock(return_value=mock_user)

    result = await account_service.disable_mfa("user-id")
    assert result == mock_user
    mock_repo.save.assert_not_called()

async def test_disable_mfa_not_found_user(
        account_service: AccountService,
        mock_repo: MagicMock
) -> None:
    mock_repo.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(NotFoundException, match="User not found"):
        await account_service.disable_mfa("user-id")

async def test_enable_mfa_not_found_user(
        account_service: AccountService,
        mock_repo: MagicMock
) -> None:
    mock_repo.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(NotFoundException, match="User not found"):
        await account_service.enable_mfa("user-id")


async def test_forgot_password_not_found_user_early_return(
        account_service: AccountService,
        mock_repo: MagicMock
) -> None:
    mock_repo.get_active_by_identifier = AsyncMock(return_value=None)

    await account_service.forgot_password("nonexist@example.com", MagicMock())

    mock_repo.save.assert_not_called()


async def test_resend_activation_code_not_found_user(
        account_service: AccountService,
        mock_repo: MagicMock
) -> None:
    mock_user = MagicMock(spec=User)
    identifier = mock_user.username
    mock_repo.get_by_identifier = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="User not found"):
        await account_service.resend_activation_code(identifier, MagicMock())

async def test_resend_activation_code_if_user_is_active(
        account_service: AccountService,
        mock_repo: MagicMock
) -> None:
    mock_user = MagicMock(spec=User)
    identifier = mock_user.username
    mock_user.is_active = True
    mock_repo.get_by_identifier = AsyncMock(return_value=mock_user)

    with pytest.raises(ValidationException, match="User already activated"):
        await account_service.resend_activation_code(identifier, MagicMock())


async def test_reset_password_invalid_token(
        account_service: AccountService,
        mock_repo: MagicMock
) -> None:
    mock_repo.get_by_reset_token = AsyncMock(return_value=False)
    with pytest.raises(NotFoundException, match="Invalid token"):
        await account_service.reset_password("invalid-token", "new-password")

async def test_reset_password_token_expired(
        account_service: AccountService,
        mock_repo: MagicMock
) -> None:
    expired_token = datetime.now(timezone.utc) - timedelta(minutes=60)
    mock_user = MagicMock(spec=User)
    mock_user.reset_password_expires_at = expired_token
    mock_repo.get_by_reset_token = AsyncMock(return_value=mock_user)

    with pytest.raises(ValidationException, match="Reset token password expired"):
        await account_service.reset_password("token-expired", "new-password")

async def test_delete_user_not_found(
        account_service: AccountService,
        mock_repo: MagicMock
) -> None:
    mock_repo.get_by_identifier = AsyncMock(return_value=None)
    with pytest.raises(NotFoundException, match="User not found"):
        await account_service.delete_user("user-id")


def test_generate_mfa_setup_missing_mfa_secret(
        account_service: AccountService,
        mock_repo: MagicMock
) -> None:
    mock_user = MagicMock(spec=User)
    mock_user.mfa_secret = None

    with pytest.raises(ValidationException, match="Mfa secret not initialized"):
        account_service._generate_mfa_secret(mock_user)







