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
    return Settings() #type: ignore

SettingsDep = Annotated[Settings, Depends(get_settings)]

@lru_cache()
def get_user_repository() -> UserRepository:
    return UserRepository()

UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]

@lru_cache()
def get_fastmail(settings: SettingsDep) -> FastMail:
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

@lru_cache()
def get_email_service(mailer: FastMailDep) -> EmailService:
    return EmailService(mailer)

EmailServiceDep = Annotated[EmailService, Depends(get_email_service)]

@lru_cache()
def get_auth_service(repository: UserRepoDep) -> AuthService:
    return AuthService(repository)

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

@lru_cache()
def get_account_service(repository: UserRepoDep, email: EmailServiceDep, settings: SettingsDep) -> AccountService:
    return AccountService(repository, email, settings)

AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
