from typing import Any, Dict

from core.app_state import AppState
from core.config import AuthConfig
from core.singleton import SingletonMeta
from database.models import User
from services.auth import AuthService


class MFAManager(metaclass=SingletonMeta):
    def __init__(self, config: AuthConfig):
        self.config = config
        self.auth_service = AuthService()
        self.state = AppState()

    @staticmethod
    def should_prompt_mfa(user: User) -> bool:
        return bool(user.mfa_enabled)

    def store_pending_auth(self, user_data: Dict[str, Any]) -> None:
        """
        Store a pending authentication state while user completes MFA.
        Resets the MFA attempts counter.
        """
        if not isinstance(user_data, dict):
            raise ValueError("user_data must be a dict")
        if "id" not in user_data:
            raise ValueError("pending user_data must include id")
        self.state.pending_user = user_data
        self.state.awaiting_mfa = True
        self.state.mfa_attempts = 0

    def get_remaining_attempts(self) -> int:
        """Return how many MFA attempts are left."""
        used = self.state.mfa_attempts
        remaining = self.config.MAX_MFA_ATTEMPTS - used
        return max(0, remaining)

    def increment_attempts(self) -> None:
        """Increment the MFA attempts counter."""
        self.state.increment_mfa_attempts()

    def is_max_attempts_reached(self) -> bool:
        """Check if the MFA attempts have reached the configured maximum."""
        return self.state.mfa_attempts >= self.config.MAX_MFA_ATTEMPTS

    def clear_mfa_state(self) -> None:
        """Clear pending MFA state."""
        self.state.clear_pending_auth()
        self.state.mfa_attempts = 0
