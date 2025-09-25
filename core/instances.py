"""
Centralized singleton instances for core services.

Usage:
    from core.instances import app_state, session_manager, auth_service

Override in tests by patching these imports.
Do not import modules here that import this file to avoid circular imports.
"""

from core.app_state import AppState
from core.mfa_manager import MFAManager
from core.session_manager import SessionManager
from database.db import db
from services.auth import AuthService

# Create singletons
app_state = AppState()
auth_service = AuthService(db.get_session)
session_manager = SessionManager(app_state=app_state, auth_service=auth_service)
mfa_manager = MFAManager(session_manager.config)

__all__ = ["app_state", "auth_service", "session_manager", "mfa_manager"]
