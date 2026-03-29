from users.respositories.user_repository import UserRepository
from users.services.email_service import EmailService
from users.services.user_service import UserService
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
def get_user_service(repository: UserRepoDep, email: EmailServiceDep) -> UserService:
    return UserService(repository, email)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]
