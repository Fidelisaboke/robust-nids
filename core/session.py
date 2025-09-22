from datetime import datetime
from typing import Dict, Any, Optional

import streamlit as st

from core.config import AuthConfig, SessionKeys
from database.models import User
from services.auth import AuthService


class SessionManager:
    """Handles auth sessions with cookie persistence."""

    def __init__(self, config: AuthConfig = AuthConfig()):
        self.config = config
        self.auth_service = AuthService()
        self._init_session_state()

    def _init_session_state(self):
        """Initialize all required session state keys."""
        if SessionKeys.USER not in st.session_state:
            st.session_state[SessionKeys.USER] = self._get_default_user()

    @staticmethod
    def _get_default_user() -> dict:
        """Return default unauthenticated user structure."""
        return {
            "id": None,
            "email": None,
            "roles": [],
            "login_time": None,
            "last_activity": None,
        }

    @staticmethod
    def get_user_info() -> Dict[str, Any]:
        """Get current user information with type safety."""
        return st.session_state.get(SessionKeys.USER, {})

    def get_user_email(self) -> Optional[str]:
        """Safely get user email."""
        return self.get_user_info().get("email")

    @property
    def is_session_valid(self) -> bool:
        """Comprehensive session validation."""
        user = st.session_state[SessionKeys.USER]

        if not user["id"] or not user["login_time"]:
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

    @staticmethod
    def login_user(user: User):
        now_ts = datetime.now().timestamp()
        roles = [role.name for role in user.roles]
        st.session_state[SessionKeys.USER] = {
            "id": user.id,
            "email": user.email,
            "roles": roles,
            "login_time": now_ts,
            "last_activity": now_ts,
        }

    def logout_user(self, reason="Logged out"):
        st.session_state[SessionKeys.USER] = self._get_default_user()
        st.warning(reason)
        st.markdown('<meta http-equiv="refresh" content="0;url=/">', unsafe_allow_html=True)
        st.rerun()

    @staticmethod
    def is_awaiting_mfa() -> bool:
        return st.session_state.get(SessionKeys.AWAITING_MFA, False)

    @staticmethod
    def get_pending_user():
        return st.session_state.get(SessionKeys.PENDING_USER, None)

    @staticmethod
    def clear_pending_auth():
        keys_to_remove = [SessionKeys.PENDING_USER, SessionKeys.AWAITING_MFA, SessionKeys.MFA_ATTEMPTS]
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]

    def refresh_session(self):
        """Update last activity timestamp if authenticated."""
        if self.is_session_valid:
            st.session_state[SessionKeys.USER]["last_activity"] = datetime.now().timestamp()

    def time_remaining(self):
        """Return time left (seconds) before session expiry."""
        user = st.session_state[SessionKeys.USER]
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
            st.session_state["user"]["last_activity"] = datetime.now().timestamp()
            return True
        return False
