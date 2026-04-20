from apigateway.clients.users_client import UsersClient


class AdminService:
    """
    Service layer for administrative operations in the API gateway.

    This service provides admin-level actions and delegates
    requests to the Users service via UsersClient.
    """

    def __init__(self, users_client: UsersClient):
        """
        Initialize AdminService.

        Args:
            users_client (UsersClient): Client used to communicate with the Users service.
        """
        self.users_client = users_client

    async def delete_user(self, identifier: str) -> None:
        """
        Delete a user account.

        Args:
            identifier (str): Username or email identifying the user.

        Returns:
            None
        """
        await self.users_client.delete_user(identifier)