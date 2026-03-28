from fastapi_mail import ConnectionConfig
from users.core.config import settings
from pydantic import SecretStr

email_settings = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=SecretStr(settings.MAIL_PASSWORD),
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True
)