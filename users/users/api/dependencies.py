from users.respositories.user_repository import UserRepository
from users.services.account_service import AccountService
from users.services.auth_service import AuthService
from users.services.email_service import EmailService
from users.core.email import email_settings
from functools import lru_cache
from fastapi_mail import FastMail
from typing import Annotated
from fastapi import Depends


@lru_cache()
def get_user_repository() -> UserRepository:
    return UserRepository()

UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]

@lru_cache()
def get_fastmail() -> FastMail:
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
def get_account_service(repository: UserRepoDep, email: EmailServiceDep) -> AccountService:
    return AccountService(repository, email)

AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
