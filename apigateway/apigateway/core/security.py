from datetime import datetime, timedelta, timezone
from apigateway.core.config import settings
from jose import jwt # type: ignore

def create_access_token(subject: str) -> str:
    utc_now = datetime.now(timezone.utc)
    expire = utc_now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(subject),
        "type": "access",
        "exp": expire,
        "iat": utc_now
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)

