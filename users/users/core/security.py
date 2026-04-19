from passlib.context import CryptContext  # type: ignore

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password using the configured password hashing scheme.

    This function uses Passlib's CryptContext with Argon2 to securely
    hash user passwords before storing them in the database.

    Args:
        password (str): The plaintext password to hash.

    Returns:
        str: The resulting hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.

    This function checks whether the provided plaintext password matches
    the stored hashed password using the configured hashing scheme.

    Args:
        plain_password (str): The plaintext password provided by the user.
        hashed_password (str): The previously hashed password from storage.

    Returns:
        bool: True if the password is correct, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)