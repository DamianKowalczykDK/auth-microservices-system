from apigateway.clients.users_client import UsersClient
from apigateway.domain.schemas import UserCreate, UserRead, UserResetPassword


class AccountService:
    def __init__(self, users_client: UsersClient):
        self.users_client = users_client

    async def create_user(self, create_user: UserCreate) -> UserRead:
        return await self.users_client.create_user(create_user)

    async def activate_user(self, code: str) -> UserRead:
        return await self.users_client.activate_user(code)

    async def resend_activation_code(self, code: str) -> dict[str, str]:
        return await self.users_client.resend_activation_code(code)

    async def forgot_password(self, identifier: str) -> dict[str, str]:
        return await self.users_client.forgot_password(identifier)

    async def reset_password(self, user_reset_password: UserResetPassword) -> dict[str, str]:
        return await self.users_client.reset_password(user_reset_password)
