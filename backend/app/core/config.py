"""
Configuration module for the backend application.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn


class Settings(BaseSettings):
    """
    Application settings using Pydantic BaseSettings for environment variable management.
    """

    # Load environment variables from .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Application settings
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    DEBUG: bool = Field(False, env="DEBUG")

    # Database settings
    DB_HOST: str = Field("localhost", env="DB_HOST")
    DB_PORT: int = Field(5432, env="DB_PORT")
    DB_NAME: str = Field("nids_db", env="DB_NAME")
    DB_USER: str = Field("nids_user", env="DB_USER")
    DB_PASSWORD: str = Field("change_this_in_production", env="DB_PASSWORD")
    DATABASE_URL: PostgresDsn = Field(..., env="DATABASE_URL")

    # Database Admin credentials (for DB setup)
    DB_ADMIN_USER: str = Field("postgres", env="DB_ADMIN_USER")
    DB_ADMIN_PASSWORD: str = Field("admin_password", env="DB_ADMIN_PASSWORD")


settings = Settings()
