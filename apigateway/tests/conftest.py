from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from apigateway.api.dependencies import get_settings
from apigateway.core.config import Settings
from apigateway.core.security import create_access_token, create_refresh_token
from apigateway.main import app


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings(
        USERS_SERVICE_URL= "http://mock-users-service",
        JWT_SECRET_KEY= "secret_key",
        JWT_ALGORITHM="HS256",
        HTTP_TIMEOUT = 5,
        ACCESS_TOKEN_EXPIRE_MINUTES= 15,
        REFRESH_TOKEN_EXPIRE_MINUTES= 60
    )

@pytest_asyncio.fixture
async def client(test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_settings] = lambda: test_settings

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def user_token(test_settings: Settings) -> str:
    return create_access_token(
        "test_user",
        secret_key=test_settings.JWT_SECRET_KEY,
        algorithm=test_settings.JWT_ALGORITHM,
        expire_minutes=10
    )

@pytest.fixture
def admin_token(test_settings: Settings) -> str:
    return create_access_token(
        "test_admin",
        secret_key=test_settings.JWT_SECRET_KEY,
        algorithm=test_settings.JWT_ALGORITHM,
        expire_minutes=10
    )

@pytest.fixture
def refresh_token(test_settings: Settings) -> str:
    return create_refresh_token(
        "test_user",
        secret_key=test_settings.JWT_SECRET_KEY,
        algorithm=test_settings.JWT_ALGORITHM,
        expire_minutes=10
    )
