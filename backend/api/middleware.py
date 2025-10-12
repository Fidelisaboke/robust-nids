import logging

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.services.exceptions.base import ServiceException
from backend.services.exceptions.mfa import MFAException
from backend.services.exceptions.user import (
    EmailAlreadyExistsError,
    UserException,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)

EXCEPTION_TO_STATUS_CODE = {
    UserNotFoundError: status.HTTP_404_NOT_FOUND,
    EmailAlreadyExistsError: status.HTTP_409_CONFLICT,
    UsernameAlreadyExistsError: status.HTTP_409_CONFLICT,
    UserException: status.HTTP_400_BAD_REQUEST,
    MFAException: status.HTTP_400_BAD_REQUEST,
    ServiceException: status.HTTP_400_BAD_REQUEST,
}


class ServiceExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except ServiceException as exc:
            # Look up the status code in the dictionary, default to 400
            status_code = EXCEPTION_TO_STATUS_CODE.get(type(exc), status.HTTP_400_BAD_REQUEST)

            logger.warning(
                f"Service Exception Handled: Status={status_code}, "
                f"Detail='{exc.detail}', Path={request.url.path}"
            )

            return JSONResponse(
                status_code=status_code,
                content={"detail": exc.detail}
            )
