from typing import TypedDict, Literal

class UserReadDict(TypedDict):
    id: str
    username: str
    email: str
    role: Literal["admin", "user"]
    is_active: bool
    mfa_secret: str | None

class MfaSetupDict(TypedDict):
    user_id: str
    provisioning_uri: str
    qr_code_base64: str