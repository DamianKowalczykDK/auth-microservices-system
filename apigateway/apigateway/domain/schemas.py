from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    identifier: str
    password: str

class UserRead(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str
    is_active: bool
    mfa_secret: str | None = None

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str

class MfaRequired(BaseModel):
    mfa_required: bool = True
    user_id: str
    mfa_secret: str | None = None

class MfaVerify(BaseModel):
    user_id: str
    code: str




