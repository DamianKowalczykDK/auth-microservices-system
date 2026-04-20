from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings for authentication and external services.

    This class defines environment-based configuration including
    service communication, JWT authentication parameters, and timeouts.
    """

    DEBUG: bool = False
    """Flag indicating whether debug mode is enabled."""

    USERS_SERVICE_URL: str
    """Base URL of the external users service."""

    HTTP_TIMEOUT: float
    """Timeout (in seconds) for HTTP requests to external services."""

    JWT_SECRET_KEY: str
    """Secret key used to sign JWT tokens."""

    JWT_ALGORITHM: str
    """Algorithm used for encoding and decoding JWT tokens."""

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    """Expiration time (in minutes) for access tokens."""

    REFRESH_TOKEN_EXPIRE_MINUTES: int
    """Expiration time (in minutes) for refresh tokens."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        frozen=True
    )
    """
    Pydantic configuration:
    - Loads environment variables from `.env` file
    - Ignores unknown fields
    - Makes settings immutable
    """