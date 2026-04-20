from apigateway.clients.users_client import UsersClient
from apigateway.domain.schemas import UserCreate, UserRead, UserResetPassword


class AccountService:
    """
    Service layer for account-related operations in the API gateway.

    This service acts as a proxy between the API layer and the Users service,
    delegating requests to the UsersClient.
    """

    def __init__(self, users_client: UsersClient):
        """
        Initialize AccountService.

        Args:
            users_client (UsersClient): Client used to communicate with the Users service.
        """
        self.users_client = users_client

    async def create_user(self, create_user: UserCreate) -> UserRead:
        """
        Create a new user account.

        Args:
            create_user (UserCreate): User registration data.

        Returns:
            UserRead: Created user.
        """
        return await self.users_client.create_user(create_user)

    async def activate_user(self, code: str) -> UserRead:
        """
        Activate a user account.

        Args:
            code (str): Activation code.

        Returns:
            UserRead: Activated user.
        """
        return await self.users_client.activate_user(code)

    async def resend_activation_code(self, code: str) -> dict[str, str]:
        """
        Resend activation code to a user.

        Args:
            code (str): Username or email.

        Returns:
            dict[str, str]: Confirmation message.
        """
        return await self.users_client.resend_activation_code(code)

    async def forgot_password(self, identifier: str) -> dict[str, str]:
        """
        Initiate password reset process.

        Args:
            identifier (str): Username or email.

        Returns:
            dict[str, str]: Confirmation message.
        """
        return await self.users_client.forgot_password(identifier)

    async def reset_password(self, user_reset_password: UserResetPassword) -> dict[str, str]:
        """
        Reset a user's password.

        Args:
            user_reset_password (UserResetPassword): Reset token and new password.

        Returns:
            dict[str, str]: Confirmation message.
        """
        return await self.users_client.reset_password(user_reset_password)