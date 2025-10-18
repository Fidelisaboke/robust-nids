from api.exception_handlers.email import email_delivery_exception_handler
from api.exception_handlers.mfa import mfa_bad_request_handler
from api.exception_handlers.user import (
    user_bad_request_handler,
    user_conflict_handler,
    user_not_found_handler,
)
from services.exceptions import email as email_exceptions
from services.exceptions import mfa as mfa_exceptions
from services.exceptions import user as user_exceptions

exc_handlers = {
    # User Exception Handlers
    user_exceptions.UserNotFoundError: user_not_found_handler,
    user_exceptions.EmailAlreadyExistsError: user_conflict_handler,
    user_exceptions.UsernameAlreadyExistsError: user_conflict_handler,
    user_exceptions.RoleNotFoundError: user_bad_request_handler,
    user_exceptions.RoleNotAssignedError: user_bad_request_handler,
    # MFA Exception Handlers
    mfa_exceptions.InvalidMFAVerificationCodeError: mfa_bad_request_handler,
    mfa_exceptions.InvalidMFARecoveryTokenError: mfa_bad_request_handler,
    mfa_exceptions.MFAAlreadyEnabledError: mfa_bad_request_handler,
    mfa_exceptions.MFANotEnabledError: mfa_bad_request_handler,
    # Email Exception Handlers
    email_exceptions.EmailDeliveryException: email_delivery_exception_handler,
}
