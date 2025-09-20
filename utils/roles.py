from enum import Enum

class SystemRoles(Enum):
    """Enum for system roles."""
    VIEWER = "viewer"
    ANALYST = "analyst"
    MANAGER = "manager"
    ADMIN = "admin"
