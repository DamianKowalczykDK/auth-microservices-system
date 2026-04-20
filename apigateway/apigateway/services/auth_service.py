from fastapi import HTTPException
from apigateway.clients.users_client import UsersClient
from apigateway.core.config import Settings
from apigateway.domain.schemas import UserLogin, TokenPair, MfaRequired, MfaVerify, TokenPayload
from apigateway.core.security import create_access_token, create_refresh_token


class AuthService:
    """
    Service responsible for authentication logic in the API gateway.

    This service coordinates authentication with the Users service,
    handles MFA flow, and generates JWT access and refresh tokens.
    """

    def __init__(self, users_client: UsersClient, settings: Settings) -> None:
        """
        Initialize AuthService.

        Args:
            users_client (UsersClient): Client for communication with Users service.
            settings (Settings): Application configuration with JWT settings.
        """
        self.users_client = users_client
        self.settings = settings

    async def login(self, user_login: UserLogin) -> TokenPair | MfaRequired:
        """
        Authenticate user and return tokens or MFA requirement.

        Args:
            user_login (UserLogin): Login credentials.

        Returns:
            TokenPair | MfaRequired: JWT tokens if authentication succeeds,
            or MFA requirement if MFA is enabled.

        Raises:
            HTTPException: If user is inactive.
        """
        user = await self.users_client.login(user_login)

        if not user.is_active:
            raise HTTPException(status_code=400, detail="User is inactive")

        if user.mfa_secret:
            return MfaRequired(user_id=user.id)

        return self._generate_tokens(user.id)

    async def verify_mfa(self, mfa_verify: MfaVerify) -> TokenPair:
        """
        Verify MFA code and generate tokens.

        Args:
            mfa_verify (MfaVerify): MFA verification payload.

        Returns:
            TokenPair: Generated JWT tokens.
        """
        user = await self.users_client.verify_user_mfa(mfa_verify)
        return self._generate_tokens(user.id)

    async def refresh_token(self, token: TokenPayload) -> TokenPair:
        """
        Refresh JWT tokens using a valid refresh token payload.

        Args:
            token (TokenPayload): Decoded JWT payload.

        Returns:
            TokenPair: New JWT tokens.

        Raises:
            HTTPException: If user is inactive.
        """
        user = await self.users_client.get_user_by_id(token.sub)

        if not user.is_active:
            raise HTTPException(status_code=400, detail="User is inactive")

        return self._generate_tokens(user.id)

    def _generate_tokens(self, user_id: str) -> TokenPair:
        """
        Generate access and refresh tokens for a user.

        Args:
            user_id (str): User identifier.

        Returns:
            TokenPair: Generated JWT tokens.
        """
        secret = self.settings.JWT_SECRET_KEY
        algorithm = self.settings.JWT_ALGORITHM

        access_token = create_access_token(
            user_id,
            secret,
            algorithm,
            self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        refresh_token = create_refresh_token(
            user_id,
            secret,
            algorithm,
            self.settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )

        return TokenPair(access_token=access_token, refresh_token=refresh_token)