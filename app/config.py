import os
import secrets

from pydantic import BaseSettings


class Settings(BaseSettings):
    DOMAIN: str
    TG_BOT_USERNAME: str
    VK_GROUP_USERNAME: str

    SECRET_KEY: str = secrets.token_urlsafe(32)
    DEFAULT_ADMIN_LOGIN: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"
    MONGO_DB: str
    MONGODB_CONNECTION_URL: str

    ACCESS_TOKEN_EXPIRATION_TIME: int = 5 * 24 * 60 * 60  # 5 days

    LOG_INCOMING_EVENTS: bool = True

    TG_TOKEN: str = ""
    VK_TOKEN: str = ""

    VK_API_VERSION: str = "5.87"
    VK_CONFIRMATION_TOKEN: str = ""
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: str = ""

    class Config:
        case_sensitive = True


settings = Settings()
