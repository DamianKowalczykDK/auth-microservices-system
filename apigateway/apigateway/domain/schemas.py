from typing import Annotated, Literal
from pydantic import BaseModel, EmailStr, Field

Password = Annotated[str, Field(min_length=6)]
Username = Annotated[str, Field(min_length=3, max_length=64, description="Unique username")]
Identifier = Annotated[str, Field(min_length=3, max_length=64, description="Username or email")]

class UserCreate(BaseModel):
    username: Username
    email: EmailStr
    password: Password
    password_confirmation: Password
    role: Literal["admin", "user"] = "user"

class UserLogin(BaseModel):
    identifier: str
    password: str

class UserResetPassword(BaseModel):
    token : str
    new_password: Password

class UserRead(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: Literal["admin", "user"] = "user"
    is_active: bool
    mfa_secret: str | None = None

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str

class TokenPayload(BaseModel):
    sub: str
    type: str

class MfaSetup(BaseModel):
    user_id: str
    provisioning_uri: str
    qr_code_base64: str


class MfaRequired(BaseModel):
    mfa_required: bool = True
    user_id: str

class MfaVerify(BaseModel):
    user_id: str
    code: str




