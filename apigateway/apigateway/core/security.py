from datetime import datetime, timedelta, timezone
from jose import jwt  # type: ignore


def create_access_token(subject: str, secret_key: str, algorithm: str, expire_minutes: int) -> str:
    """
    Create a JWT access token.

    Args:
        subject (str): Identifier of the token subject (e.g., user ID).
        secret_key (str): Secret key used to sign the token.
        algorithm (str): JWT signing algorithm.
        expire_minutes (int): Token expiration time in minutes.

    Returns:
        str: Encoded JWT access token.
    """
    return _create_token(subject, "access", secret_key, algorithm, expire_minutes)


def create_refresh_token(subject: str, secret_key: str, algorithm: str, expire_minutes: int) -> str:
    """
    Create a JWT refresh token.

    Args:
        subject (str): Identifier of the token subject (e.g., user ID).
        secret_key (str): Secret key used to sign the token.
        algorithm (str): JWT signing algorithm.
        expire_minutes (int): Token expiration time in minutes.

    Returns:
        str: Encoded JWT refresh token.
    """
    return _create_token(subject, "refresh", secret_key, algorithm, expire_minutes)


def _create_token(
        subject: str,
        token_type: str,
        secret_key: str,
        algorithm: str,
        expire_minutes: int,
) -> str:
    """
    Internal helper function to generate JWT tokens.

    Args:
        subject (str): Identifier of the token subject.
        token_type (str): Type of token ("access" or "refresh").
        secret_key (str): Secret key used for signing.
        algorithm (str): JWT algorithm.
        expire_minutes (int): Expiration time in minutes.

    Returns:
        str: Encoded JWT token.
    """
    utc_now = datetime.now(timezone.utc)
    expire = utc_now + timedelta(minutes=expire_minutes)

    to_encode = {
        "sub": subject,
        "type": token_type,
        "exp": expire,
        "iat": utc_now
    }

    return jwt.encode(to_encode, secret_key, algorithm)