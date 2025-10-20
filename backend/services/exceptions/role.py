from services.exceptions.base import ServiceException


class RoleException(ServiceException):
    """Base class for role-related errors."""

    def __init__(self, detail: str = "A role-related error occurred."):
        super().__init__(detail)


class RoleNotFoundError(RoleException):
    """Raised when a role is not found in the database."""

    def __init__(self, detail: str = "Role not found."):
        super().__init__(detail)
