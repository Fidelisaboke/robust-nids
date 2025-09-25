"""
Centralized singleton instances for core services.

Usage:
    from core.instances import app_state, session_manager, mfa_manager, auth_service

Override in tests by patching these imports.
Do not import modules here that import this file to avoid circular imports.
"""

from core.app_state import AppState
from core.session_manager import SessionManager
from core.mfa_manager import MFAManager
from services.auth import AuthService
from database.db import db

app_state = AppState()
session_manager = SessionManager()
mfa_manager = MFAManager()
auth_service = AuthService(db.get_session)
