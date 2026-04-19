from pydantic import SecretStr
from users.core.config import Settings
from users.respositories.user_repository import UserRepository
from users.services.account_service import AccountService
from users.services.auth_service import AuthService
from users.services.email_service import EmailService
from functools import lru_cache
from fastapi_mail import FastMail, ConnectionConfig
from fastapi import Depends
from typing import Annotated


@lru_cache()
def get_settings() -> Settings:
    """
    Provide application settings as a cached FastAPI dependency.

    This function loads configuration from environment variables (via Settings)
    and caches the result to avoid repeated instantiation.

    Returns:
        Settings: Application configuration instance.
    """
    return Settings()  # type: ignore


SettingsDep = Annotated[Settings, Depends(get_settings)]
"""FastAPI dependency type for application settings."""


@lru_cache()
def get_user_repository() -> UserRepository:
    """
    Provide a cached instance of UserRepository.

    Returns:
        UserRepository: Repository for user database operations.
    """
    return UserRepository()


UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]
"""FastAPI dependency type for UserRepository."""


@lru_cache()
def get_fastmail(settings: SettingsDep) -> FastMail:
    """
    Create and provide a configured FastMail instance.

    Args:
        settings (Settings): Application settings dependency.

    Returns:
        FastMail: Configured email client.
    """
    email_settings = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=SecretStr(settings.MAIL_PASSWORD),
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=True
    )
    return FastMail(email_settings)


FastMailDep = Annotated[FastMail, Depends(get_fastmail)]
"""FastAPI dependency type for FastMail client."""


@lru_cache()
def get_email_service(mailer: FastMailDep) -> EmailService:
    """
    Provide EmailService instance.

    Args:
        mailer (FastMail): Configured FastMail client.

    Returns:
        EmailService: Service responsible for sending emails.
    """
    return EmailService(mailer)


EmailServiceDep = Annotated[EmailService, Depends(get_email_service)]
"""FastAPI dependency type for EmailService."""


@lru_cache()
def get_auth_service(repository: UserRepoDep) -> AuthService:
    """
    Provide AuthService instance.

    Args:
        repository (UserRepository): User repository dependency.

    Returns:
        AuthService: Service responsible for authentication logic.
    """
    return AuthService(repository)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
"""FastAPI dependency type for AuthService."""


@lru_cache()
def get_account_service(
        repository: UserRepoDep,
        email: EmailServiceDep,
        settings: SettingsDep
) -> AccountService:
    """
    Provide AccountService instance.

    Args:
        repository (UserRepository): User repository dependency.
        email (EmailService): Email service dependency.
        settings (Settings): Application settings dependency.

    Returns:
        AccountService: Service handling user account operations.
    """
    return AccountService(repository, email, settings)


AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
"""FastAPI dependency type for AccountService."""