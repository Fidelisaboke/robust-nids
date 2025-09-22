"""
Configuration module for the NIDS Dashboard application.

This module centralizes all application configuration settings including:
- Database connection parameters and URL construction
- Authentication and session management settings
- Application environment and debug settings
- Streamlit session state key constants

All configuration is environment-aware, reading from environment variables
with appropriate fallback values for development.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AppConfig:
    """App-wide settings."""

    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")


@dataclass(frozen=True)
class DatabaseConfig:
    """Database configuration."""

    HOST: str = os.getenv("DB_HOST", "localhost")
    PORT: int = int(os.getenv("DB_PORT", "5432"))
    NAME: str = os.getenv("DB_NAME", "nids_db")
    USER: str = os.getenv("DB_USER", "nids_user")
    PASSWORD: str = os.getenv("DB_PASSWORD", "")
    ADMIN_USER: str = os.getenv("ADMIN_USER", "postgres")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")
    URL: str = (
        f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )


@dataclass(frozen=True)
class AuthConfig:
    """Auth configuration."""

    IDLE_TIMEOUT: ClassVar[int] = 130
    ABSOLUTE_TIMEOUT: ClassVar[int] = 8 * 3600
    GRACE_THRESHOLD: ClassVar[int] = 120
    MAX_MFA_ATTEMPTS: ClassVar[int] = 3
    MFA_CODE_LENGTH: ClassVar[int] = 6


class SessionKeys(str, Enum):
    """Keys for Streamlit session state."""

    USER = "user"
    PENDING_USER = "pending_user"
    AWAITING_MFA = "awaiting_mfa"
    MFA_ATTEMPTS = "mfa_attempts"
