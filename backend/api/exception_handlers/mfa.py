from fastapi import Request, status
from fastapi.responses import JSONResponse

from services.exceptions.mfa import (
    InvalidMFARecoveryTokenError,
    InvalidMFAVerificationCodeError,
    MFAAlreadyEnabledError,
    MFANotEnabledError,
)


async def mfa_bad_request_handler(
    request: Request,
    exc: (
        MFAAlreadyEnabledError
        | MFANotEnabledError
        | InvalidMFAVerificationCodeError
        | InvalidMFARecoveryTokenError
    ),
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.detail},
    )
