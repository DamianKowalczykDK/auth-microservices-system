from apigateway.clients.users_client import UsersClient

class AdminService:
    def __init__(self, users_client: UsersClient):
        self.users_client = users_client

    async def delete_user(self, identifier: str) -> None:
        await self.users_client.delete_user(identifier)
