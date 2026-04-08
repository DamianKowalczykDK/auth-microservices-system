from fastapi import HTTPException
from apigateway.clients.users_client import UsersClient
from apigateway.core.config import Settings
from apigateway.domain.schemas import UserLogin, TokenPair, MfaRequired, MfaVerify, TokenPayload
from apigateway.core.security import create_access_token, create_refresh_token

class AuthService:
    def __init__(self, users_client: UsersClient, settings: Settings) -> None:
        self.users_client = users_client
        self.settings = settings

    async def login(self, user_login: UserLogin) -> TokenPair | MfaRequired:
        user = await self.users_client.login(user_login)

        if not user.is_active:
            raise HTTPException(status_code=400, detail="User is inactive")

        if user.mfa_secret:
            return MfaRequired(user_id=user.id)

        return self._generate_tokens(user.id)

    async def verify_mfa(self, mfa_verify: MfaVerify) -> TokenPair:
        user = await self.users_client.verify_user_mfa(mfa_verify)
        return self._generate_tokens(user.id)

    async def refresh_token(self, token: TokenPayload) -> TokenPair:
        user = await self.users_client.get_user_by_id(token.sub)

        if not user.is_active:
            raise HTTPException(status_code=400, detail="User is inactive")

        return self._generate_tokens(user.id)

    def _generate_tokens(self, user_id: str) -> TokenPair:
        secret = self.settings.JWT_SECRET_KEY
        algorithm = self.settings.JWT_ALGORITHM

        access_token = create_access_token(user_id, secret, algorithm, self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token = create_refresh_token(user_id, secret, algorithm, self.settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)


