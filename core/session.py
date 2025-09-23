from datetime import datetime
from typing import Dict, Any, Optional

import streamlit as st

from core.config import AuthConfig, SessionKeys
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

        # Initialise MFA-related session state
        if "mfa_enabled" not in st.session_state:
            st.session_state.mfa_enabled = False
        if "mfa_setup_complete" not in st.session_state:
            st.session_state.mfa_setup_complete = False

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
            "mfa_method": None,
            "profile_complete": False,
        }

    @staticmethod
    def get_user_info() -> Dict[str, Any]:
        """Get current user information from the session state with type safety."""
        return st.session_state.get(SessionKeys.USER, {})

    def get_user_id(self) -> Optional[int]:
        """Safely get user ID."""
        user_id = self.get_user_info().get("id", None)
        return user_id

    def get_user_email(self) -> Optional[str]:
        """Safely get user email."""
        return self.get_user_info().get("email")

    def update_user_profile(self, profile_data: Dict[str, Any]):
        """Update user profile data in session state."""
        if self.get_user_id():
            st.session_state[SessionKeys.USER].update(profile_data)
            # Refresh from database to ensure consistency
            self._refresh_user_data()

    def _refresh_user_data(self):
        """Refresh user data from database to keep session state in sync."""
        user_id = self.get_user_id()
        if user_id:
            user_profile = self.auth_service.get_user_profile(user_id)
            if user_profile:
                st.session_state[SessionKeys.USER].update(user_profile)

    @staticmethod
    def login_user(user_data: Dict[str, Any]):
        """Login user with enhanced profile data."""
        now_ts = datetime.now().timestamp()

        # Ensure we have all required fields with defaults
        login_data = {
            "id": user_data.get("id"),
            "email": user_data.get("email"),
            "username": user_data.get("username"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "phone": user_data.get("phone"),
            "department": user_data.get("department"),
            "job_title": user_data.get("job_title"),
            "timezone": user_data.get("timezone", "UTC"),
            "preferences": user_data.get("preferences", {}),
            "roles": user_data.get("roles", []),
            "mfa_enabled": user_data.get("mfa_enabled", False),
            "mfa_method": user_data.get("mfa_method"),
            "profile_completed": user_data.get("profile_completed", False),
            "login_time": now_ts,
            "last_activity": now_ts,
        }

        st.session_state[SessionKeys.USER] = login_data

        # Sync MFA session state
        st.session_state.mfa_enabled = login_data["mfa_enabled"]
        st.session_state.mfa_setup_complete = login_data["mfa_enabled"]

    def logout_user(self, reason="Logged out"):
        """Logout user and clear all session data."""
        # Clear MFA-related session state
        mfa_keys = ["mfa_enabled", "mfa_setup_complete", "show_mfa_setup", "temp_mfa_secret"]
        for key in mfa_keys:
            if key in st.session_state:
                del st.session_state[key]

        st.session_state[SessionKeys.USER] = self._get_default_user()
        st.warning(reason)
        st.markdown('<meta http-equiv="refresh" content="0;url=/">', unsafe_allow_html=True)
        st.rerun()

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

    def requires_mfa(self) -> bool:
        """Check if current user requires MFA verification."""
        user = self.get_user_info()
        return user.get("mfa_enabled", False)

    def verify_mfa(self, code: str) -> bool:
        """Verify MFA token for pending user."""
        if not self.is_awaiting_mfa():
            return False

        pending_user = self.get_pending_user()
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
            attempts = st.session_state.get(SessionKeys.MFA_ATTEMPTS, 0) + 1
            st.session_state[SessionKeys.MFA_ATTEMPTS] = attempts

            if attempts >= self.config.MAX_MFA_ATTEMPTS:
                self.clear_pending_auth()
                st.error("Too many failed MFA attempts. Please try logging in again.")
            return False

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
