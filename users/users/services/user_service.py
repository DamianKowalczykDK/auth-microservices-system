from datetime import datetime, timedelta, timezone
from users.domain.schemas import UserCreate, UserLogin
from users.domain.models import User
from users.respositories.user_repository import UserRepository
from users.services.email_service import EmailService
from users.core.security import get_password_hash, verify_password
from users.core.config import settings
from users.core.exceptions import ValidationException, ApiException, NotFoundException, ConflictException
import uuid
import pyotp
import base64
import io
import qrcode #type: ignore

class UserService:
    def __init__(self, repository: UserRepository, email: EmailService) -> None:
        self.repository = repository
        self.email = email

    async def create_user(self, user_create: UserCreate) -> User:

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
        await self.email.send_activation_email(user.email, activation_code)
        return created_user
