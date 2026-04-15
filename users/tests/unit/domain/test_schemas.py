import pytest
from users.domain.schemas import UserCreate


def test_create_user_validate_password() -> None:
    with pytest.raises(ValueError, match="Passwords don't match"):
        _ = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password",
            password_confirmation="password1"
        )