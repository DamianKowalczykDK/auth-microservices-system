from datetime import datetime, timedelta, timezone
from jose import jwt # type: ignore

def create_access_token(subject: str, secret_key: str, algorithm: str, expire_minutes:int) -> str:
    return _create_token(subject, "access", secret_key, algorithm, expire_minutes)

def create_refresh_token(subject: str, secret_key: str, algorithm: str, expire_minutes:int) -> str:
    return _create_token(subject, "refresh",secret_key, algorithm, expire_minutes)


def _create_token(
        subject: str,
        token_type: str,
        secret_key: str,
        algorithm: str,
        expire_minutes: int,
) -> str:
    utc_now = datetime.now(timezone.utc)
    expire = utc_now + timedelta(minutes=expire_minutes)
    to_encode = {
        "sub": subject,
        "type": token_type,
        "exp": expire,
        "iat": utc_now
    }
    return jwt.encode(to_encode, secret_key, algorithm)

