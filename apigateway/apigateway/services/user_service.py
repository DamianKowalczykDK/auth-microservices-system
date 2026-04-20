from apigateway.clients.users_client import UsersClient
from apigateway.domain.schemas import UserRead, MfaSetup


class UserService:
    """
    Service layer for user-related operations in the API gateway.

    This service acts as a thin abstraction over the UsersClient,
    providing methods for retrieving user data and managing MFA.
    """

    def __init__(self, users_client: UsersClient):
        """
        Initialize UserService.

        Args:
            users_client (UsersClient): Client used to communicate with the Users service.
        """
        self.users_client = users_client

    async def get_user_by_id(self, user_id: str) -> UserRead:
        """
        Retrieve a user by their unique identifier.

        Args:
            user_id (str): User ID.

        Returns:
            UserRead: User data.
        """
        return await self.users_client.get_user_by_id(user_id)

    async def enable_mfa(self, user_id: str) -> MfaSetup:
        """
        Enable multi-factor authentication for a user.

        Args:
            user_id (str): User ID.

        Returns:
            MfaSetup: MFA setup data including QR code and provisioning URI.
        """
        return await self.users_client.enable_mfa(user_id)

    async def disable_mfa(self, user_id: str) -> UserRead:
        """
        Disable multi-factor authentication for a user.

        Args:
            user_id (str): User ID.

        Returns:
            UserRead: Updated user data after disabling MFA.
        """
        return await self.users_client.disable_mfa(user_id)