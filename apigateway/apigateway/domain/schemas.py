from typing import Annotated, Literal
from pydantic import BaseModel, EmailStr, Field

Password = Annotated[str, Field(min_length=6)]
"""Password type with minimum length constraint."""

Username = Annotated[str, Field(min_length=3, max_length=64, description="Unique username")]
"""Username type with length constraints and uniqueness intent."""

Identifier = Annotated[str, Field(min_length=3, max_length=64, description="Username or email")]
"""Identifier used for login (username or email)."""


class UserCreate(BaseModel):
    """
    Schema for user registration request.

    Contains required fields for creating a new user account.
    """

    username: Username
    email: EmailStr
    password: Password
    password_confirmation: Password
    role: Literal["admin", "user"] = "user"


class UserLogin(BaseModel):
    """
    Schema for user login request.
    """

    identifier: str
    password: str


class UserResetPassword(BaseModel):
    """
    Schema for resetting user password using a token.
    """

    token: str
    new_password: Password


class UserRead(BaseModel):
    """
    Schema representing user data returned from the API.
    """

    id: str
    username: str
    email: EmailStr
    role: Literal["admin", "user"] = "user"
    is_active: bool
    mfa_secret: str | None = None


class TokenPair(BaseModel):
    """
    Schema representing a pair of JWT tokens (access + refresh).
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPairResponse(BaseModel):
    """
    Schema representing response with only access token.
    """

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """
    Schema representing decoded JWT payload.
    """

    sub: str
    type: str


class MfaSetup(BaseModel):
    """
    Schema returned during MFA setup process.

    Contains provisioning URI and QR code.
    """

    user_id: str
    provisioning_uri: str
    qr_code_base64: str


class MfaRequired(BaseModel):
    """
    Schema indicating that MFA verification is required.
    """

    mfa_required: bool = True
    user_id: str


class MfaVerify(BaseModel):
    """
    Schema for verifying MFA code.
    """

    user_id: str
    code: str