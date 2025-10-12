from backend.services.exceptions.base import ServiceException


class MFAException(ServiceException):
    """Base class for MFA-related errors."""

    def __init__(self, detail: str = 'An MFA error occurred.'):
        super().__init__(detail)


class MFAAlreadyEnabledError(MFAException):
    """Raised when trying to enable MFA for a user who already has it enabled."""

    def __init__(self, detail: str = 'MFA is already enabled for this user.'):
        super().__init__(detail)


class MFANotEnabledError(MFAException):
    """Raised when an MFA action is attempted for a user without MFA."""

    def __init__(self, detail: str = 'MFA is not enabled for this user.'):
        super().__init__(detail)


class InvalidMFAVerificationCodeError(MFAException):
    """Raised when a provided TOTP or backup code is invalid."""

    def __init__(self, detail: str = 'Invalid MFA verification code.'):
        super().__init__(detail)


class InvalidMFARecoveryTokenError(MFAException):
    """Raised when an MFA recovery token is invalid or expired."""

    def __init__(self, detail: str = 'Invalid or expired MFA recovery token.'):
        super().__init__(detail)
