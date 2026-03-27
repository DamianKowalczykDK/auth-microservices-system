from datetime import datetime
from typing import Annotated, Literal, Self
from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict


Password = Annotated[str, Field(min_length=6)]
Username = Annotated[str, Field(min_length=3, max_length=64, description="Unique username")]
Identifier = Annotated[str, Field(min_length=3, max_length=64, description="Username or email")]

class UserCreate(BaseModel):
    username: Username
    email: EmailStr
    password: Password
    password_confirmation: Password
    role: Literal["admin", "user"] = "user"

    @model_validator(mode="after")
    def validate_password(self) -> Self:
        if self.password != self.password_confirmation:
            raise ValueError("Passwords don't match")
        return self


class UserRead(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: EmailStr
    role: str
    is_active: str
    created_at: datetime
    mfa_secret: str

class UserLogin(BaseModel):
    identifier: Identifier
    password: str

class UserResetPassword(BaseModel):
    token : str
    new_password: Password

class MfaSetup(BaseModel):
    user_id: str
    provisioning_uri: str
    qr_code_base64: str

class ErrorApi(BaseModel):
    error: str
    detail: list[str] | None = None