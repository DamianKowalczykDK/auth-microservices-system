from users.core.exceptions import ValidationException, NotFoundException, ConflictException
from users.domain.schemas import UserCreate, UserLogin, MfaSetup, MfaVerify
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


    async def reset_password(self, token: str, new_password: str) -> None:
        user = await self.repository.get_by_reset_token(token)
        if not user or not user.reset_password_expires_at:
            raise NotFoundException("Invalid token")

        if user.reset_password_expires_at < datetime.now(timezone.utc):
            raise ValidationException("Reset token password expired")

        user.password_hash = get_password_hash(new_password)
        user.reset_password_token = None
        user.reset_password_expires_at = None

        await self.repository.save(user)

    async def enable_mfa(self, user_id: str) -> MfaSetup:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        secret = pyotp.random_base32()
        user.mfa_secret = secret
        await self.repository.save(user)

        return self._generate_mfa_secret(user)

    async def disable_mfa(self, user_id: str) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        if not user.mfa_secret:
            raise ValidationException("User has no mfa secret")
        user.mfa_secret = None
        return await self.repository.save(user)

    async  def verify_user_mfa(self, mfa_verify: MfaVerify) -> User:
        user = await self.repository.get_by_id(mfa_verify.user_id)
        if not user:
            raise NotFoundException("User not found")
        if not user.mfa_secret:
            raise ValidationException("User has no mfa secret")
        if not self._verify_mfa_code(user.mfa_secret, mfa_verify.code):
            raise ValidationException("Invalid MFA code")
        return user

    async def get_user_by_id(self, user_id: str) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user


    async def delete_user(self, identifier: str) -> None:
        user = await self.repository.get_by_identifier(identifier)
        if not user:
            raise NotFoundException("User not found")
        await self.repository.delete(user)

    # PRIVATE METHODS

    def _verify_mfa_code(self, mfa_security: str, code: str) -> bool:
        totp = pyotp.TOTP(mfa_security)
        return totp.verify(code, valid_window=1)

    def _generate_mfa_secret(self, user: User) -> MfaSetup:
        if not user.mfa_secret:
            raise ValidationException("Mfa secret not initialized")
        totp = pyotp.TOTP(user.mfa_secret)

        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name="FastAPI Security"
        )

        qr = qrcode.QRCode(box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")

        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return MfaSetup(
            user_id=str(user.id),
            provisioning_uri=provisioning_uri,
            qr_code_base64=qr_code_base64
        )







