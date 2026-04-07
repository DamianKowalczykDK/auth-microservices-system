import pyotp
import qrcode  # type: ignore

from users.core.exceptions import ValidationException, NotFoundException
from users.core.security import verify_password
from users.domain.models import User
from users.domain.schemas import UserLogin, MfaVerify
from users.respositories.user_repository import UserRepository


class AuthService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository


    async  def verify_user_mfa(self, mfa_verify: MfaVerify) -> User:
        user = await self.repository.get_by_id(mfa_verify.user_id)
        if not user:
            raise NotFoundException("User not found")
        if not user.mfa_secret:
            raise ValidationException("User has no mfa secret")
        if not self._verify_mfa_code(user.mfa_secret, mfa_verify.code):
            raise ValidationException("Invalid MFA code")
        return user

    async def verify_credentials(self, user_login: UserLogin) -> User:
        user = await self.repository.get_active_by_identifier(user_login.identifier)
        if not user or not verify_password(user_login.password, user.password_hash):
            raise ValidationException("Invalid credentials")
        return user

    def _verify_mfa_code(self, mfa_security: str, code: str) -> bool:
        totp = pyotp.TOTP(mfa_security)
        return totp.verify(code, valid_window=1)

