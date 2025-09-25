from datetime import datetime
from typing import Dict, Any, Optional

import streamlit as st


from core.config import AuthConfig
from core.singleton import SingletonMeta
from core.instances import app_state, auth_service


class SessionManager(metaclass=SingletonMeta):
    """Handles auth sessions in the app."""

    def __init__(self, config: AuthConfig = AuthConfig()):
        self.config = config
        self.auth_service = auth_service
        self.app_state = app_state

    @staticmethod
    def _get_default_user() -> dict:
        """Return default unauthenticated user structure."""
        return {
            # Authentication fields
            "id": None,
            "email": None,
            "username": None,
            "roles": [],
            "login_time": None,
            "last_activity": None,
            # Profile fields
            "first_name": None,
            "last_name": None,
            "phone": None,
            "department": None,
            "job_title": None,
            "timezone": "UTC",
            # Preferences
            "preferences": {},
            # MFA Status
            "mfa_enabled": False,
            "mfa_setup_complete": False,
            "mfa_method": None,
            "profile_complete": False,
        }

    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information from the session state with type safety."""
        return self.app_state.user

    def get_user_id(self) -> Optional[int]:
        """Safely get user ID."""
        user_id = self.app_state.user.get("id", None)
        return user_id

    def get_user_email(self) -> Optional[str]:
        """Safely get user email."""
        user_email = self.app_state.user.get("email", None)
        return user_email

    def update_user_profile(self, profile_data: Dict[str, Any]):
        """Update user profile data in session state."""
        uid = self.get_user_id()
        if not uid:
            return

        user = dict(self.app_state.user)
        user.update(profile_data)
        self.app_state.user = user

        # Refresh from database to ensure consistency
        fresh = self.auth_service.get_user_profile(uid)
        if fresh:
            fresh_user = dict(user)
            fresh_user.update(fresh)
            self.app_state.user = fresh_user

    def login_user(self, user_data: Dict[str, Any]):
        """Login user with enhanced profile data."""
        now_ts = datetime.now().timestamp()
        login_data = {**self._get_default_user(), **user_data, "login_time": now_ts, "last_activity": now_ts}
        self.app_state.user = login_data
        self.clear_pending_auth()

    def logout_user(self, reason="Logged out"):
        """Logout user and clear all session data."""
        # Clear MFA-related session state
        self.app_state.reset_all()
        st.warning(reason)
        st.markdown('<meta http-equiv="refresh" content="0;url=/">', unsafe_allow_html=True)
        st.rerun()

    @property
    def is_session_valid(self) -> bool:
        """Comprehensive session validation."""
        user = dict(self.app_state.user)

        if not user.get("id") or not user.get("login_time"):
            return False

        return not self._is_session_expired(user)

    def _is_session_expired(self, user: dict) -> bool:
        """Check if session has expired due to timeout."""
        now = datetime.now()
        login_time = datetime.fromtimestamp(user["login_time"])
        last_activity = datetime.fromtimestamp(user["last_activity"])

        # Check absolute timeout
        if (now - login_time).total_seconds() > self.config.ABSOLUTE_TIMEOUT:
            self.logout_user("Session expired (absolute timeout)")
            return True

        # Check idle timeout
        if (now - last_activity).total_seconds() > self.config.IDLE_TIMEOUT:
            self.logout_user("Session expired (idle timeout)")
            return True

        return False

    def requires_mfa(self) -> bool:
        """Check if current user requires MFA verification."""
        user = self.get_user_info()
        return bool(user.get("mfa_enabled"))

    def verify_mfa(self, code: str) -> bool:
        """Verify MFA token for pending user."""
        if not self.app_state.awaiting_mfa:
            return False

        pending_user = self.app_state.pending_user
        if not pending_user:
            return False

        user_id = pending_user.get("id")
        if not user_id:
            return False

        # Verify token
        if self.auth_service.verify_totp(user_id, code):
            # MFA successful, complete login
            self.login_user(pending_user)
            self.clear_pending_auth()
            return True
        else:
            # Track failed attempts
            self.app_state.increment_mfa_attempts()
            if self.app_state.mfa_attempts >= self.config.MAX_MFA_ATTEMPTS:
                self.clear_pending_auth()
                st.error("Too many failed MFA attempts. Please try logging in again.")
            return False

    def is_awaiting_mfa(self) -> bool:
        return self.app_state.awaiting_mfa

    def get_pending_user(self) -> dict:
        return self.app_state.pending_user

    def clear_pending_auth(self):
        self.app_state.clear_pending_auth()

    def refresh_session(self):
        """Update last activity timestamp if authenticated."""
        if self.is_session_valid:
            user = dict(self.app_state.user)
            user["last_activity"] = datetime.now().timestamp()
            self.app_state.user = user

    def time_remaining(self) -> int:
        """Return time left (seconds) before session expiry."""
        user = dict(self.app_state.user)
        if not user["id"]:
            return 0

        now = datetime.now()
        login_time = datetime.fromtimestamp(user["login_time"])
        last_activity = datetime.fromtimestamp(user["last_activity"])
        idle_remaining = self.config.IDLE_TIMEOUT - (now - last_activity).total_seconds()
        abs_remaining = self.config.ABSOLUTE_TIMEOUT - (now - login_time).total_seconds()

        return int(min(idle_remaining, abs_remaining))

    def needs_grace_prompt(self):
        """Return True if session is close to expiring."""
        return self.time_remaining() <= self.config.GRACE_THRESHOLD

    def extend_session(self):
        """Extend session by refreshing last_activity timestamp."""
        if self.is_session_valid:
            user = dict(self.app_state.user)
            user["last_activity"] = datetime.now().timestamp()
            self.app_state.user = user
            return True
        return False
