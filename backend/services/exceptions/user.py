from services.exceptions.base import ServiceException


class UserException(ServiceException):
    """Base class for user-related errors."""

    def __init__(self, detail: str = 'A user-related error occurred.'):
        super().__init__(detail)


class UserNotFoundError(UserException):
    """Raised when a user is not found in the database."""

    def __init__(self, detail: str = 'User not found.'):
        super().__init__(detail)


class EmailAlreadyExistsError(UserException):
    """Raised when trying to create a user with an email that already exists."""

    def __init__(self, detail: str = 'Email is already registered.'):
        super().__init__(detail)


class UsernameAlreadyExistsError(UserException):
    """Raised when trying to create a user with a username that is already taken."""

    def __init__(self, detail: str = 'Username is already taken.'):
        super().__init__(detail)


class RoleNotFoundError(UserException):
    """Raised when trying to assign a role that does not exist."""

    def __init__(self, role_id: int, detail: str = None):
        if detail is None:
            detail = f'Failed to assign role {role_id}: not found.'
        super().__init__(detail)


class RoleNotAssignedError(UserException):
    """Raised when a user is created without any roles."""

    def __init__(self, detail: str = 'At least one role must be assigned to the user.'):
        super().__init__(detail)
