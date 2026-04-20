from fastapi import FastAPI, APIRouter
from apigateway.api.routes import auth, admin, account, user
import logging


logging.basicConfig(level=logging.INFO)
"""
Basic logging configuration for the API Gateway application.
Enables INFO-level logs for runtime visibility.
"""


app = FastAPI(
    title="API Gateway",
    description="API Gateway",
    version="1.0.0"
)
"""
FastAPI application instance for the API Gateway service.
Defines global metadata such as title, description, and version.
"""


@app.get("/", response_model=dict[str, str], tags=["Root"])
async def healthcheck() -> dict[str, str]:
    """
    Healthcheck endpoint.

    Used to verify that the API Gateway service is running.

    Returns:
        dict[str, str]: Service status information.
    """
    return {
        "status": "ok",
        "service": "apigateway"
    }


router = APIRouter(prefix="/api")
"""
Main API router that aggregates all feature-specific routers
under a common `/api` prefix.
"""

router.include_router(auth.router)
"""Authentication routes."""

router.include_router(admin.router)
"""Admin routes."""

router.include_router(account.router)
"""Account management routes."""

router.include_router(user.router)
"""User-related routes."""


app.include_router(router)
"""
Attach the main API router to the FastAPI application.
"""