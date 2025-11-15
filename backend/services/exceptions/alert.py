from services.exceptions.base import ServiceException


class AlertException(ServiceException):
    """Base class for alert-related errors."""
    def __init__(self, detail: str = "An alert-related error occurred."):
        super().__init__(detail)


class AlertNotFoundError(AlertException):
    """Raised when an alert is not found in the database."""
    def __init__(self, detail: str = "Alert not found."):
        super().__init__(detail)
