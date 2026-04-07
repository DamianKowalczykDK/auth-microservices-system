from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from users.core.config import Settings
from users.domain.models import User


async def init_db(settings: Settings) -> None:
    client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGODB_URI, tz_aware=True)
    await init_beanie(database=client[settings.MONGODB_DB], document_models=[User])  # type: ignore