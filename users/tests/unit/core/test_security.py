from users.core.security import get_password_hash, verify_password


def test_verify_password() -> None:
    password = "SecretPassword"
    hashed_password = get_password_hash(password)

    assert password != hashed_password
    assert verify_password(password, hashed_password) is True
    assert verify_password("wrongpassword", hashed_password) is False