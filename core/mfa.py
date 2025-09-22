import streamlit as st

from core.config import AuthConfig, SessionKeys
from database.models import User
from services.auth import AuthService


class MFAManager:
    def __init__(self, config: AuthConfig):
        self.config = config
        self.auth_service = AuthService()

    @staticmethod
    def should_prompt_mfa(user: User) -> bool:
        return user.mfa_enabled

    @staticmethod
    def store_pending_auth(user: User):
        """Store pending authentication state for MFA."""
        st.session_state[SessionKeys.PENDING_USER] = user
        st.session_state[SessionKeys.AWAITING_MFA] = True
        st.session_state[SessionKeys.MFA_ATTEMPTS] = 0

    def get_remaining_attempts(self) -> int:
        attempts = st.session_state.get(SessionKeys.MFA_ATTEMPTS, 0)
        return max(0, self.config.MAX_MFA_ATTEMPTS - attempts)

    @staticmethod
    def increment_attempts():
        current = st.session_state.get(SessionKeys.MFA_ATTEMPTS, 0)
        st.session_state[SessionKeys.MFA_ATTEMPTS] = current + 1

    def is_max_attempts_reached(self) -> bool:
        attempts = st.session_state.get(SessionKeys.MFA_ATTEMPTS, 0)
        return attempts >= self.config.MAX_MFA_ATTEMPTS
