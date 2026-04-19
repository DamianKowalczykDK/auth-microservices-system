from datetime import datetime
from typing import Annotated, Literal, Self
from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict, BeforeValidator


Password = Annotated[str, Field(min_length=6)]
"""Password type with minimum length validation (6 characters)."""

Username = Annotated[str, Field(min_length=3, max_length=64, description="Unique username")]
"""Username type constrained by length and used as a unique identifier."""

Identifier = Annotated[str, Field(min_length=3, max_length=64, description="Username or email")]
"""Login identifier which can be either username or email."""

PyObjectId = Annotated[str, BeforeValidator(str)]
"""MongoDB ObjectId representation converted to string."""


class UserCreate(BaseModel):
    """
    Schema used for user registration.

    Contains required fields for creating a new user account,
    including password confirmation validation.
    """

    username: Username
    email: EmailStr
    password: Password
    password_confirmation: Password
    role: Literal["admin", "user"] = "user"

    @model_validator(mode="after")
    def validate_password(self) -> Self:
        """
        Ensure that password and password confirmation match.

        Raises:
            ValueError: If passwords do not match.

        Returns:
            Self: Validated model instance.
        """
        if self.password != self.password_confirmation:
            raise ValueError("Passwords don't match")
        return self


class UserRead(BaseModel):
    """
    Schema returned when reading user data from the API.

    This model is used for responses and excludes sensitive fields
    like password hashes.
    """

    model_config = ConfigDict(from_attributes=True)

    id: PyObjectId
    username: str
    email: EmailStr
    role: str
    is_active: bool
    mfa_secret: str | None = None
    created_at: datetime


class UserLogin(BaseModel):
    """
    Schema used for user authentication (login request).
    """

    identifier: Identifier
    password: str


class UserResetPassword(BaseModel):
    """
    Schema used for resetting a user's password using a token.
    """

    token: str
    new_password: Password


class MfaSetup(BaseModel):
    """
    Response schema for MFA setup process.

    Contains provisioning URI and QR code for authenticator apps.
    """

    user_id: str
    provisioning_uri: str
    qr_code_base64: str


class MfaVerify(BaseModel):
    """
    Schema used to verify MFA authentication code.
    """

    user_id: str
    code: str


class ErrorApi(BaseModel):
    """
    Standard API error response schema.

    Provides a general error message and optional detailed list
    of validation or processing errors.
    """

    error: str
    detail: list[str] | None = None