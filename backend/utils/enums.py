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


class SystemPermissions(Enum):
    """System-wide permissions that can be assigned to roles"""

    # Dashboard permissions
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_LIVE_MONITOR = "view_live_monitor"

    # Alert permissions
    VIEW_ALERTS = "view_alerts"
    UPDATE_ALERT_STATUS = "update_alert_status"
    DELETE_ALERTS = "delete_alerts"

    # Analytics permissions
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"

    # Data permissions
    VIEW_DATA_EXPLORER = "view_data_explorer"
    ACCESS_RAW_DATA = "access_raw_data"

    # Model permissions
    VIEW_MODELS = "view_models"
    TRAIN_MODELS = "train_models"
    DEPLOY_MODELS = "deploy_models"

    # System permissions
    VIEW_SETTINGS = "view_settings"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    SYSTEM_CONFIGURATION = "system_configuration"

    # Administrative permissions
    VIEW_LOGS = "view_logs"
    SYSTEM_MAINTENANCE = "system_maintenance"
