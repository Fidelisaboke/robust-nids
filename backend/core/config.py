"""
Configuration module for the backend application.
"""

from pathlib import Path
from typing import ClassVar

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / '.env'


class Settings(BaseSettings):
    """
    Application settings using Pydantic BaseSettings for environment variable management.
    Values should be set via the .env file or environment variables. Default values set
    here should not be relied upon for production deployments.
    """

    # Load environment variables from .env file
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding='utf-8')

    # Application settings
    ENVIRONMENT: str
    SECRET_KEY: str
    DEBUG: bool = False
    APP_NAME: str = 'NIDS'

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

    # PgAdmin
    PGADMIN_DEFAULT_EMAIL: str
    PGADMIN_DEFAULT_PASSWORD: str

    # Redis configuration
    REDIS_URL: str

    # CORS origins
    BACKEND_CORS_ORIGINS: list[str] = ['http://localhost', 'http://localhost:3000']

    # Default user preferences for the dashboard
    DEFAULT_USER_PREFERENCES: ClassVar[dict] = {
        'dashboard': {
            'default_view': 'overview',
            'refresh_interval': 300,
            'theme': 'system',
        },
        'notifications': {
            'email': True,
            'browser': True,
            'critical_alerts': True,
            'high_priority': True,
            'medium_priority': False,
        },
        'privacy': {'show_online_status': True, 'share_analytics': False},
    }

    # JWT
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440  # 1 day
    MFA_CHALLENGE_TOKEN_EXPIRE_MINUTES: int = 5  # 5 minutes

    # MFA Settings
    MFA_RECOVERY_TOKEN_EXPIRES_HOURS: int = 1  # 1 hour


settings = Settings()
