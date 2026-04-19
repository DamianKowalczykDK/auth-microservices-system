from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.

    This class defines all required configuration values for the application,
    including database connection details, authentication settings,
    and mail server configuration. Values are typically loaded from a `.env` file
    using Pydantic Settings.
    """

    DEBUG: bool = False
    """Flag indicating whether debug mode is enabled."""

    USER_ACTIVATION_EXPIRATION_MINUTES: int
    """Time (in minutes) before a user activation token expires."""

    RESET_PASSWORD_EXPIRATION_MINUTES: int
    """Time (in minutes) before a password reset token expires."""

    MONGODB_DB: str
    """Name of the MongoDB database."""

    MONGODB_HOST: str
    """Hostname or IP address of the MongoDB server."""

    MONGODB_PORT: int
    """Port number used to connect to MongoDB."""

    MONGODB_USERNAME: str
    """Username for MongoDB authentication."""

    MONGODB_PASSWORD: str
    """Password for MongoDB authentication."""

    @property
    def MONGODB_URI(self) -> str:
        """
        Construct and return the full MongoDB connection URI.

        Returns:
            str: MongoDB connection string including credentials and host.
        """
        return f"mongodb://{self.MONGODB_USERNAME}:{self.MONGODB_PASSWORD}@{self.MONGODB_HOST}:{self.MONGODB_PORT}"

    MAIL_SERVER: str
    """SMTP mail server address."""

    MAIL_PORT: int
    """SMTP server port."""

    MAIL_USERNAME: str
    """Username used for email authentication."""

    MAIL_PASSWORD: str
    """Password used for email authentication."""

    MAIL_STARTTLS: bool
    """Whether to use STARTTLS for email connection."""

    MAIL_SSL_TLS: bool
    """Whether to use SSL/TLS for email connection."""

    MAIL_FROM: EmailStr
    """Default sender email address."""

    MAIL_FROM_NAME: str
    """Display name for the sender email address."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", frozen=True)
    """
    Pydantic configuration:
    - Loads environment variables from `.env` file
    - Ignores extra fields not defined in the model
    - Makes the settings immutable (frozen)
    """