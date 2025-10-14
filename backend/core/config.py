"""
Configuration module for the backend application.
"""

from pathlib import Path
from typing import ClassVar

from pydantic import Field, PostgresDsn
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
    SECRET_KEY: str = Field('mysecretkey', validation_alias='SECRET_KEY')
    DEBUG: bool = Field(False, validation_alias='DEBUG')
    APP_NAME: str = Field('NIDS', validation_alias='APP_NAME')
    ENVIRONMENT: str = Field('local', validation_alias='ENVIRONMENT')

    # Database settings
    DB_HOST: str = Field('localhost', validation_alias='DB_HOST')
    DB_PORT: int = Field(5432, validation_alias='DB_PORT')
    DB_NAME: str = Field('nids_db', validation_alias='DB_NAME')
    DB_USER: str = Field('nids_user', validation_alias='DB_USER')
    DB_PASSWORD: str = Field('change_this_in_production', validation_alias='DB_PASSWORD')
    DATABASE_URL: PostgresDsn = Field(
        'postgresql://nids_user:change_this_in_production@localhost:5432/nids_db',
        validation_alias='DATABASE_URL'
    )

    # Database Admin credentials (for DB setup)
    DB_ADMIN_USER: str = Field('postgres', validation_alias='DB_ADMIN_USER')
    DB_ADMIN_PASSWORD: str = Field('admin_password', validation_alias='DB_ADMIN_PASSWORD')

    # PgAdmin
    PGADMIN_DEFAULT_EMAIL: str = Field('admin@admin.com', validation_alias='PGADMIN_DEFAULT_EMAIL')
    PGADMIN_DEFAULT_PASSWORD: str = Field('admin', validation_alias='PGADMIN_DEFAULT_PASSWORD')

    # Redis configuration
    REDIS_URL: str = Field('redis://localhost:6379/0', validation_alias='REDIS_URL')

    # CORS origins
    BACKEND_CORS_ORIGINS: list[str] = Field(
        ['http://localhost:3000'],
        validation_alias='BACKEND_CORS_ORIGINS'
    )

    # Default user preferences for the dashboard
    DEFAULT_USER_PREFERENCES: ClassVar[dict] = {
        'dashboard': {
            'default_view': 'overview',
            'refresh_interval': 300,
            'theme': 'system',
        },  # 5 minutes
        'notifications': {
            'email': True,
            'browser': True,
            'critical_alerts': True,
            'high_priority': True,
            'medium_priority': False,
        },
        'privacy': {'show_online_status': True, 'share_analytics': False},
    }

    # JWT Settings
    JWT_ALGORITHM: str = Field('HS256', validation_alias='JWT_ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, validation_alias='ACCESS_TOKEN_EXPIRE_MINUTES')  # 30 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(1440, validation_alias='REFRESH_TOKEN_EXPIRE_MINUTES')  # 1 day
    MFA_CHALLENGE_TOKEN_EXPIRE_MINUTES: int = Field(5, validation_alias='MFA_CHALLENGE_TOKEN_EXPIRE_MINUTES')

    # MFA Settings
    MFA_RECOVERY_TOKEN_EXPIRES_HOURS: int = Field(1, validation_alias='MFA_RECOVERY_TOKEN_EXPIRES_HOURS')


# noinspection PyArgumentList
settings = Settings()
