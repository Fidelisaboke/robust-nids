"""
Streamlit session state management module.
"""

import streamlit as st

from core.config import SessionKeys
from core.singleton import SingletonMeta


class AppState(metaclass=SingletonMeta):
    def __init__(self):
        self._init_defaults()

    @staticmethod
    def _init_defaults():
        """Initialise the session state with default variables."""
        defaults = {
            SessionKeys.AWAITING_MFA: False,
            SessionKeys.BACKUP_CODES: None,
            SessionKeys.MFA_ATTEMPTS: 0,
            SessionKeys.PENDING_USER: None,
            SessionKeys.SHOW_BACKUP_CODES: False,
            SessionKeys.SHOW_BACKUP_CODE_LOGIN: False,
            SessionKeys.SHOW_BACKUP_CODE_WARNING: False,
            SessionKeys.SHOW_MFA_SETUP: False,
            SessionKeys.SHOW_NEW_BACKUP_CODES: False,
            SessionKeys.TEMP_MFA_SECRET: None,
            SessionKeys.USER: None,
            SessionKeys.VERIFY_DISABLE_MFA: False,
        }
        for key, val in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = val

    @property
    def awaiting_mfa(self) -> bool:
        return bool(st.session_state.get(SessionKeys.AWAITING_MFA, False))

    @awaiting_mfa.setter
    def awaiting_mfa(self, value: bool):
        st.session_state[SessionKeys.AWAITING_MFA] = bool(value)

    @property
    def backup_codes(self) -> list[str]:
        return st.session_state.get(SessionKeys.BACKUP_CODES) or []

    @backup_codes.setter
    def backup_codes(self, value: list[str]):
        st.session_state[SessionKeys.BACKUP_CODES] = value

    @property
    def mfa_attempts(self) -> int:
        return int(st.session_state.get(SessionKeys.MFA_ATTEMPTS, 0))

    @mfa_attempts.setter
    def mfa_attempts(self, val: int):
        st.session_state[SessionKeys.MFA_ATTEMPTS] = int(val)

    def increment_mfa_attempts(self):
        self.mfa_attempts = self.mfa_attempts + 1

    @property
    def pending_user(self) -> dict:
        return st.session_state.get(SessionKeys.PENDING_USER)

    @pending_user.setter
    def pending_user(self, value: dict):
        if not isinstance(value, dict) and value is not None:
            raise ValueError("pending_user must be a dict or None")
        st.session_state[SessionKeys.PENDING_USER] = value

    @property
    def show_backup_codes(self) -> bool:
        return bool(st.session_state.get(SessionKeys.SHOW_BACKUP_CODES, False))

    @show_backup_codes.setter
    def show_backup_codes(self, value: bool):
        st.session_state[SessionKeys.SHOW_BACKUP_CODES] = bool(value)

    @property
    def show_backup_code_login(self) -> bool:
        return bool(st.session_state.get(SessionKeys.SHOW_BACKUP_CODE_LOGIN, False))

    @show_backup_code_login.setter
    def show_backup_code_login(self, value: bool):
        st.session_state[SessionKeys.SHOW_BACKUP_CODE_LOGIN] = bool(value)

    @property
    def show_backup_code_warning(self) -> bool:
        return bool(st.session_state.get(SessionKeys.SHOW_BACKUP_CODE_WARNING, False))

    @show_backup_code_warning.setter
    def show_backup_code_warning(self, value: bool):
        st.session_state[SessionKeys.SHOW_BACKUP_CODE_WARNING] = bool(value)

    @property
    def show_mfa_setup(self) -> bool:
        return bool(st.session_state.get(SessionKeys.SHOW_MFA_SETUP, False))

    @show_mfa_setup.setter
    def show_mfa_setup(self, value: bool):
        st.session_state[SessionKeys.SHOW_MFA_SETUP] = bool(value)

    @property
    def show_new_backup_codes(self) -> bool:
        return bool(st.session_state.get(SessionKeys.SHOW_NEW_BACKUP_CODES, False))

    @show_new_backup_codes.setter
    def show_new_backup_codes(self, value: bool):
        st.session_state[SessionKeys.SHOW_NEW_BACKUP_CODES] = bool(value)

    @property
    def temp_mfa_secret(self) -> str:
        return st.session_state.get(SessionKeys.TEMP_MFA_SECRET, None)

    @temp_mfa_secret.setter
    def temp_mfa_secret(self, value: str):
        st.session_state[SessionKeys.TEMP_MFA_SECRET] = value

    @property
    def user(self) -> dict:
        """
        User property stored in the app state.

        Note: When updating this dict, copy it using
        `dict(self.app_state.user)`, perform the update,
        then set the user back to the `self.app_state.user`.
        """
        return st.session_state.get(SessionKeys.USER) or {}

    @user.setter
    def user(self, value: dict):
        if not isinstance(value, dict) and value is not None:
            raise ValueError("user must be a dict or None")
        st.session_state[SessionKeys.USER] = value

    @property
    def verify_disable_mfa(self) -> bool:
        return bool(st.session_state.get(SessionKeys.VERIFY_DISABLE_MFA, False))

    @verify_disable_mfa.setter
    def verify_disable_mfa(self, value: bool):
        st.session_state[SessionKeys.VERIFY_DISABLE_MFA] = bool(value)

    def clear_pending_auth(self):
        for key in (SessionKeys.PENDING_USER, SessionKeys.AWAITING_MFA, SessionKeys.MFA_ATTEMPTS):
            if key in st.session_state:
                del st.session_state[key]

        self.awaiting_mfa = False

    def reset_all(self):
        for key in list(st.session_state.keys()):
            if key is None:
                continue
            del st.session_state[key]
        self._init_defaults()
