from unittest.mock import MagicMock, AsyncMock
from apigateway.domain.schemas import UserRead
from apigateway.services.user_service import UserService


async def test_get_user_by_id() -> None:
    mock_user_client = MagicMock()
    mock_user_client.get_user_by_id = AsyncMock(return_value=UserRead(
        id="user_id",
        username="username",
        email="test@email.example.com",
        role="user",
        is_active=False
    ))

    service = UserService(mock_user_client)
    response = await service.get_user_by_id("user_id")

    assert response.username == "username"



