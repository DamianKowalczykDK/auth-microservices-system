from fastapi import FastAPI
from users.api.dependencies import get_settings
from users.api.error_handlers import register_error_handlers
from users.core.config import Settings
from users.core.database import init_db
from users.api.routes import auth, account
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Application lifespan context manager.

    This function is executed on application startup and shutdown.
    It initializes the database connection before the application starts.

    Args:
        _ (FastAPI): FastAPI application instance (unused).

    Yields:
        None
    """
    settings: Settings = get_settings()
    await init_db(settings=settings)
    yield


app = FastAPI(
    title="Users",
    description="Users",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/", response_model=dict[str, str], tags=["Root"])
async def healthcheck() -> dict[str, str]:
    """
    Health check endpoint.

    Used to verify that the service is running.

    Returns:
        dict[str, str]: Service status information.
    """
    return {
        "status": "ok",
        "service": "users"
    }


register_error_handlers(app)
"""Register global exception handlers."""

app.include_router(auth.router)
"""Register authentication routes."""

app.include_router(account.router)
"""Register account management routes."""