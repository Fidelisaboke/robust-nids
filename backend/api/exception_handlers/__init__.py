from backend.services.exceptions import mfa as mfa_exceptions
from backend.services.exceptions import user as user_exceptions

from .mfa import mfa_bad_request_handler
from .user import user_bad_request_handler, user_conflict_handler, user_not_found_handler

exc_handlers = {
    # User Exception Handlers
    user_exceptions.UserNotFoundError: user_not_found_handler,
    user_exceptions.EmailAlreadyExistsError: user_conflict_handler,
    user_exceptions.UsernameAlreadyExistsError: user_conflict_handler,
    user_exceptions.RoleNotFoundError: user_bad_request_handler,
    user_exceptions.RoleNotAssignedError: user_bad_request_handler,
    # MFA Exception Handlers
    mfa_exceptions.MFAException: mfa_bad_request_handler,
}
