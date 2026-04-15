from unittest.mock import patch, MagicMock, AsyncMock
from users.api.dependencies import (
    get_settings,
    get_user_repository,
    get_fastmail,
    get_email_service,
    get_account_service,
    get_auth_service
)
from users.core.config import Settings
from users.main import lifespan

MOCK_ENV = {
    "MAIL_USERNAME": "mock",
    "MAIL_PASSWORD": "mock",
    "MAIL_FROM": "mock@test.com",
    "MAIL_PORT": "123",
    "MAIL_SERVER": "localhost",
    "MAIL_STARTTLS": "False",
    "MAIL_SSL_TLS": "False",
    "MONGODB_DB": "test",
    "MONGODB_HOST": "localhost",
    "MONGODB_PORT": "27017",
    "MONGODB_USERNAME": "user",
    "MONGODB_PASSWORD": "pass",
    "USER_ACTIVATION_EXPIRATION_MINUTES": "10",
    "RESET_PASSWORD_EXPIRATION_MINUTES": "10"
}

def test_dependencies_construction() -> None:
    with patch.dict("os.environ", MOCK_ENV):
        get_settings.cache_clear()
        settings = get_settings()
        repo = get_user_repository()
        fastmail = get_fastmail(settings)
        email_service = get_email_service(fastmail)
        account_service = get_account_service(repo, email_service, settings)
        auth_service = get_auth_service(repo)

    assert settings.MAIL_USERNAME == "mock"
    assert all([fastmail, email_service, account_service, auth_service])

async def test_lifespan() -> None:
    app = MagicMock()
    with patch("users.main.init_db", new_callable=AsyncMock) as mock_init_db:
        with patch("users.api.dependencies.get_settings") as mock_get_settings:
            mock_settings = MagicMock(spec=Settings)
            mock_get_settings.return_value = mock_settings

            async with lifespan(app):
                pass
            mock_init_db.assert_called_once()