from beanie import Document, Indexed
from typing import Literal
from datetime import datetime, timezone, timedelta
from pydantic import Field, EmailStr
import uuid

class User(Document):


    class Settings:
        name = "users"

    username: Indexed(str, unique=True)  # type: ignore
    email: Indexed(EmailStr, unique=True)  # type: ignore

    password_hash: str
    role: Literal["user", "admin"] = "user"
    is_active: bool = False

    activation_code: Indexed(str, unique=True) # type: ignore
    activation_created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    reset_password_token: Indexed(str, unique=True) | None = None # type: ignore
    reset_password_expires_at: datetime | None = None

    mfa_secret: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def activate(self) -> None:
        self.is_active = True
        self.activation_code = str(self.id)
        self.updated_at = datetime.now(timezone.utc)

    def update_activation_code(self) -> None:
        self.activation_code = str(uuid.uuid4())
        self.activation_created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def set_reset_password_token(self, expires_minutes: int) -> None:
        self.reset_password_token = str(uuid.uuid4())
        self.reset_password_expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        self.updated_at = datetime.now(timezone.utc)