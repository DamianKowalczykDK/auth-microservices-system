import asyncio
from typing import Generator, AsyncGenerator, Any
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from testcontainers.mongodb import MongoDbContainer #type: ignore

from users.api.dependencies import get_settings, get_email_service
from users.core.config import Settings
from users.core.database import init_db
from users.core.security import pwd_context
from users.domain.models import User
from users.main import app
from users.services.email_service import EmailService


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='session', autouse=True)
def speed_up_hashing() -> None:
    pwd_context.update(argon2__time_cost=1, argon2__memory_cost=512)

@pytest.fixture(scope='session')
def mongodb_container() -> Generator[MongoDbContainer, None, None]:
    with MongoDbContainer("mongo:7.0") as mongo:
        yield mongo
#
@pytest.fixture(scope="session")
def test_settings(mongodb_container: MongoDbContainer) -> Settings:
    return Settings(
        DEBUG=True,
        USER_ACTIVATION_EXPIRATION_MINUTES=15,
        RESET_PASSWORD_EXPIRATION_MINUTES=15,
        MONGODB_DB="test_db",
        MONGODB_HOST=mongodb_container.get_container_host_ip(),
        MONGODB_PORT=int(mongodb_container.get_exposed_port(27017)),
        MONGODB_USERNAME="test",
        MONGODB_PASSWORD="test",
        MAIL_SERVER="mock",
        MAIL_PORT=123,
        MAIL_USERNAME="mock",
        MAIL_PASSWORD="mock",
        MAIL_FROM="mock@test.com",
        MAIL_FROM_NAME="Test",
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=False
    )

@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_db_test(test_settings: Settings, event_loop: asyncio.AbstractEventLoop) -> AsyncGenerator[None, Any]:
    await init_db(test_settings)
    yield

@pytest.fixture
def mock_email_service() -> MagicMock:
    return MagicMock(spec=EmailService)


@pytest_asyncio.fixture
async def client(test_settings: Settings, mock_email_service: MagicMock) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_settings] = lambda: test_settings
    app.dependency_overrides[get_email_service] = lambda: mock_email_service

    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    await User.find_all().delete()
    app.dependency_overrides.clear()
