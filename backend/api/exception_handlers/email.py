"""
Exception handlers related to email operations.
"""

from fastapi import Request
from fastapi.responses import JSONResponse

from services.exceptions.email import EmailDeliveryException


def email_delivery_exception_handler(request: Request, exc: EmailDeliveryException):
    """
    Handles EmailDeliveryException and returns a JSON error response.
    """
    return JSONResponse(status_code=500, content={"detail": str(exc) or "Email delivery failed."})
