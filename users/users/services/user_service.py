from users.core.exceptions import ValidationException, ApiException, NotFoundException, ConflictException
from users.domain.schemas import UserCreate, UserLogin
from users.domain.models import User
from users.respositories.user_repository import UserRepository
from users.services.email_service import EmailService
from users.core.security import get_password_hash, verify_password
from users.core.config import settings
from datetime import datetime, timedelta, timezone
from fastapi import BackgroundTasks
import uuid
import pyotp
import base64
import io
import qrcode #type: ignore

class UserService:
    def __init__(self, repository: UserRepository, email: EmailService) -> None:
        self.repository = repository
        self.email = email

    async def create_user(self, user_create: UserCreate, bg_tasks: BackgroundTasks) -> User:

        if await self.repository.get_by_email(user_create.email):
            raise ConflictException("Email already exists")

        if await self.repository.get_by_username(user_create.username):
            raise ConflictException("Username already exists")

        activation_code = str(uuid.uuid4())
        user = User(
            username=user_create.username,
            email=user_create.email,
            password_hash=get_password_hash(user_create.password),
            role=user_create.role,
            activation_code=activation_code
        )

        created_user = await self.repository.create(user)
        bg_tasks.add_task(self.email.send_activation_email, user.email, activation_code)
        return created_user

    async def activate_user(self, code: str) -> User:
        user = await self.repository.get_by_activation_code(code)
        if not user:
            raise NotFoundException("Invalid activation code")

        expiration_minutes = settings.USER_ACTIVATION_EXPIRATION_MINUTES
        now_utc = datetime.now(timezone.utc)

        if user.activation_created_at + timedelta(minutes=expiration_minutes) < now_utc:
            raise ValidationException("Activation code expired")

        user.activate()
        return await self.repository.save(user)

    async def resend_activation_code(self, identifier: str, bg_tasks: BackgroundTasks) -> User:
        user = await self.repository.get_by_identifier(identifier)
        if not user:
            raise NotFoundException("User not found")

        if user.is_active:
            raise ValidationException("User already activated")

        user.update_activation_code()
        await self.repository.save(user)

        bg_tasks.add_task(self.email.send_activation_email, user.email, user.activation_code)

        return user

    async def verify_credentials(self, user_login: UserLogin) -> User:
        user = await self.repository.get_active_by_identifier(user_login.identifier)
        if not user or not verify_password(user_login.password, user.password_hash):
            raise ValidationException("Invalid credentials")
        return user

    async def forgot_password(self, identifier: str, bg_tasks: BackgroundTasks) -> None:
        user = await self.repository.get_active_by_identifier(identifier)
        if not user:
            return

        user.set_reset_password_token(settings.RESET_PASSWORD_EXPIRATION_MINUTES)
        await self.repository.save(user)

        html = f"<p>Reset token: {user.reset_password_token}</p>"

        bg_tasks.add_task(self.email.send_email, user.email, "Password Reset", html)





