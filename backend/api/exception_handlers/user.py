from fastapi import Request, status
from fastapi.responses import JSONResponse

from services.exceptions.user import (
    EmailAlreadyExistsError,
    RoleNotAssignedError,
    RoleNotFoundError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)


async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.detail},
    )


async def user_conflict_handler(
    request: Request, exc: (EmailAlreadyExistsError | UsernameAlreadyExistsError)
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.detail},
    )


async def user_bad_request_handler(request: Request, exc: (RoleNotFoundError | RoleNotAssignedError)):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.detail},
    )
