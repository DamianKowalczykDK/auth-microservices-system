from beanie import Document, Indexed
from typing import Literal
from datetime import datetime, timezone, timedelta
from pydantic import Field, EmailStr
import uuid


class User(Document):
    """
    User database model stored in MongoDB via Beanie ODM.

    This model represents an application user, including authentication
    credentials, activation and password reset mechanisms, role-based
    access control, and optional MFA configuration.
    """

    class Settings:
        """
        Beanie-specific configuration for the document.

        Attributes:
            name (str): Name of the MongoDB collection.
        """
        name = "users"

    username: Indexed(str, unique=True)  # type: ignore
    """Unique username used for authentication and identification."""

    email: Indexed(EmailStr, unique=True)  # type: ignore
    """Unique email address of the user."""

    password_hash: str
    """Hashed password stored securely (never plaintext)."""

    role: Literal["user", "admin"] = "user"
    """Role of the user defining access level in the system."""

    is_active: bool = False
    """Indicates whether the user account is activated."""

    activation_code: Indexed(str, unique=True)  # type: ignore
    """Unique activation code used to activate the user account."""

    activation_created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    """Timestamp when the activation code was generated."""

    reset_password_token: Indexed(str, unique=True) | None = None  # type: ignore
    """Token used for password reset operations."""

    reset_password_expires_at: datetime | None = None
    """Expiration time for the password reset token."""

    mfa_secret: str | None = None
    """Optional secret used for multi-factor authentication."""

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    """Timestamp when the user was created."""

    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    """Timestamp when the user was last updated."""

    def activate(self) -> None:
        """
        Activate the user account.

        Marks the user as active and refreshes the activation code and update timestamp.
        """
        self.is_active = True
        self.activation_code = str(self.id)
        self.updated_at = datetime.now(timezone.utc)

    def update_activation_code(self) -> None:
        """
        Generate a new activation code for the user.

        Updates the activation code and resets the activation timestamp.
        """
        self.activation_code = str(uuid.uuid4())
        self.activation_created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def set_reset_password_token(self, expires_minutes: int) -> None:
        """
        Set a password reset token with an expiration time.

        Args:
            expires_minutes (int): Time in minutes until the reset token expires.
        """
        self.reset_password_token = str(uuid.uuid4())
        self.reset_password_expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=expires_minutes
        )
        self.updated_at = datetime.now(timezone.utc)