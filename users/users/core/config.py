from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr

class Settings(BaseSettings):
    DEBUG: bool = False

    USER_ACTIVATION_EXPIRATION_MINUTES: int
    RESET_PASSWORD_EXPIRATION_MINUTES: int

    MONGODB_DB: str
    MONGODB_HOST: str
    MONGODB_PORT: int
    MONGODB_USERNAME: str
    MONGODB_PASSWORD: str

    @property
    def MONGODB_URI(self) -> str:
        return f"mongodb://{self.MONGODB_USERNAME}:{self.MONGODB_PASSWORD}@{self.MONGODB_HOST}:{self.MONGODB_PORT}"

    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    MAIL_FROM: EmailStr
    MAIL_FROM_NAME: str


    model_config = SettingsConfigDict(env_file=".env", extra="ignore", frozen=True)
