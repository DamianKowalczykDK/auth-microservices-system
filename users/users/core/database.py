from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from users.core.config import Settings
from users.domain.models import User


async def init_db(settings: Settings) -> None:
    """
    Initialize the MongoDB database connection and configure Beanie ODM.

    This function creates an asynchronous MongoDB client using the provided
    application settings, then initializes Beanie with the specified database
    and document models.

    Args:
        settings (Settings): Application configuration containing MongoDB
            connection details and database name.

    Returns:
        None
    """
    client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGODB_URI, tz_aware=True)
    await init_beanie(database=client[settings.MONGODB_DB], document_models=[User])  # type: ignore