"""
Configuration module for the backend application.
"""

import os
from pathlib import Path
from typing import ClassVar

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

# Dynamically select .env or .env.test based on ENVIRONMENT
_env = os.environ.get("ENVIRONMENT", None)
if _env == "test":
    ENV_FILE = BASE_DIR / ".env.test"
else:
    ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """
    Application settings using Pydantic BaseSettings for environment variable management.
    Values should be set via the .env file or environment variables. Default values set
    here should not be relied upon for production deployments.
    """

    # Load environment variables from .env file
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")

    # Application settings
    ENVIRONMENT: str
    SECRET_KEY: str
    DEBUG: bool = False
    APP_NAME: str = "NIDS"

    # Database settings
    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DATABASE_URL: PostgresDsn

    # Database Admin credentials (for DB setup)
    DB_ADMIN_USER: str
    DB_ADMIN_PASSWORD: str

    # Email Settings
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str = "NIDS System"
    MAIL_PORT: int = 587
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    TEMPLATE_FOLDER: Path = BASE_DIR / "templates" / "email"
    SUPPORT_EMAIL: str

    # PgAdmin
    PGADMIN_DEFAULT_EMAIL: str
    PGADMIN_DEFAULT_PASSWORD: str

    # Redis configuration
    REDIS_URL: str

    # Frontend configuration
    FRONTEND_URL: str = "http://localhost:3000"

    # CORS origins
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost", "http://localhost:3000"]

    # Default user preferences for the dashboard
    DEFAULT_USER_PREFERENCES: ClassVar[dict] = {
        "dashboard": {
            "default_view": "overview",
            "refresh_interval": 300,
            "theme": "system",
        },
        "notifications": {
            "email": True,
            "browser": True,
            "critical_alerts": True,
            "high_priority": True,
            "medium_priority": False,
        },
        "privacy": {"show_online_status": True, "share_analytics": False},
    }

    # JWT Settings
    JWT_ALGORITHM: str = "HS256"

    # Token Expiration Times (in minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440
    MFA_CHALLENGE_TOKEN_EXPIRE_MINUTES: int = 5
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 15

    # MFA Recovery Token Expiration (in hours)
    MFA_RECOVERY_TOKEN_EXPIRES_HOURS: int = 1


# noinspection PyArgumentList
settings = Settings()
