from datetime import datetime, timedelta, timezone
from apigateway.core.config import settings
from jose import jwt # type: ignore

def create_access_token(subject: str) -> str:
    return _create_token(settings.ACCESS_TOKEN_EXPIRE_MINUTES, subject, token_type="access")

def create_refresh_token(subject: str) -> str:
    return _create_token(settings.REFRESH_TOKEN_EXPIRE_MINUTES, subject, token_type="refresh")


def _create_token(expire_minutes: int, subject: str, token_type: str) -> str:
    utc_now = datetime.now(timezone.utc)
    expire = utc_now + timedelta(minutes=expire_minutes)
    to_encode = {
        "sub": subject,
        "type": token_type,
        "exp": expire,
        "iat": utc_now
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)

