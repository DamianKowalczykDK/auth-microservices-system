import pyotp
import qrcode  # type: ignore
from users.core.exceptions import ValidationException, NotFoundException
from users.core.security import verify_password
from users.domain.models import User
from users.domain.schemas import UserLogin, MfaVerify
from users.respositories.user_repository import UserRepository


class AuthService:
    """
    Service responsible for authentication and MFA verification logic.

    This service handles user credential validation and multi-factor
    authentication (MFA) checks using TOTP.
    """

    def __init__(self, repository: UserRepository) -> None:
        """
        Initialize AuthService.

        Args:
            repository (UserRepository): Repository used for user retrieval.
        """
        self.repository = repository

    async def verify_user_mfa(self, mfa_verify: MfaVerify) -> User:
        """
        Verify a user's MFA code and return the user if valid.

        Args:
            mfa_verify (MfaVerify): MFA verification data including user ID and code.

        Returns:
            User: Authenticated user.

        Raises:
            NotFoundException: If user does not exist.
            ValidationException: If MFA is not configured or code is invalid.
        """
        user = await self.repository.get_by_id(mfa_verify.user_id)
        if not user:
            raise NotFoundException("User not found")

        if not user.mfa_secret:
            raise ValidationException("User has no mfa secret")

        if not self._verify_mfa_code(user.mfa_secret, mfa_verify.code):
            raise ValidationException("Invalid MFA code")

        return user

    async def verify_credentials(self, user_login: UserLogin) -> User:
        """
        Verify user login credentials (username/email + password).

        Args:
            user_login (UserLogin): Login request containing identifier and password.

        Returns:
            User: Authenticated active user.

        Raises:
            ValidationException: If credentials are invalid.
        """
        user = await self.repository.get_active_by_identifier(user_login.identifier)
        if not user or not verify_password(user_login.password, user.password_hash):
            raise ValidationException("Invalid credentials")

        return user

    def _verify_mfa_code(self, mfa_security: str, code: str) -> bool:
        """
        Validate a Time-based One-Time Password (TOTP) MFA code.

        Args:
            mfa_security (str): MFA secret key.
            code (str): Code provided by the user.

        Returns:
            bool: True if code is valid, False otherwise.
        """
        totp = pyotp.TOTP(mfa_security)
        return totp.verify(code, valid_window=1)