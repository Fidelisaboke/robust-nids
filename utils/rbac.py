from functools import wraps

import streamlit as st

from core.session_manager import SessionManager
from services.permissions import permission_service
from utils.permissions import SystemPermissions

session_manager = SessionManager()


def has_permission(user_id, permission_name):
    """Check if a user has a specific permission"""
    return permission_service.user_has_permission(user_id, permission_name)


def permission_required(required_permission):
    """Decorator to protect routes based on permissions"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not session_manager.is_session_valid:
                st.error("Please log in to access this page")
                st.stop()

            user_id = session_manager.get_user_id()
            if user_id is None or not has_permission(user_id, required_permission):
                st.error("You don't have permission to access this page")
                st.stop()

            return func(*args, **kwargs)

        return wrapper

    return decorator


# Create specific permission decorators for common actions
def can_view_dashboard(func):
    return permission_required(SystemPermissions.VIEW_DASHBOARD.value)(func)


def can_view_alerts(func):
    return permission_required(SystemPermissions.VIEW_ALERTS.value)(func)


def can_manage_users(func):
    return permission_required(SystemPermissions.MANAGE_USERS.value)(func)


def can_configure_system(func):
    return permission_required(SystemPermissions.SYSTEM_CONFIGURATION.value)(func)


# Helper function to check multiple permissions
def has_any_permission(user_id, permission_names):
    """Check if user has any of the specified permissions"""
    return any(has_permission(user_id, perm) for perm in permission_names)


def has_all_permissions(user_id, permission_names):
    """Check if user has all specified permissions"""
    return all(has_permission(user_id, perm) for perm in permission_names)
