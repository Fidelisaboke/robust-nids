from enum import Enum


class SystemRoles(Enum):
    """Enum for system roles."""

    VIEWER = "viewer"
    ANALYST = "analyst"
    MANAGER = "manager"
    ADMIN = "admin"


class MFAMethod(Enum):
    """Enum for MFA methods."""

    TOTP = "totp"
