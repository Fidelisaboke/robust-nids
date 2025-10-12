"""
Dependencies for user-dependent routes and operations.
"""

import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer

from backend.core.config import settings
from backend.core.dependencies import get_user_repository
from backend.database.models import User
from backend.database.repositories.user import UserRepository

# HTTP Bearer scheme for MFA challenge token extraction
http_bearer_scheme = HTTPBearer()


async def get_current_user(
        credentials=Security(http_bearer_scheme),
        user_repo: UserRepository = Depends(get_user_repository),
):
    """Retrieve the current user based on the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    # Extract the token from the credentials
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        # Ensure the token is an access token
        if payload.get('token_type') != 'access':
            raise credentials_exception

        user_id = int(payload.get('sub'))
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user


async def get_user_from_mfa_challenge_token(
        credentials=Security(http_bearer_scheme), user_repo: UserRepository = Depends(get_user_repository)
):
    """Retrieve user from MFA challenge token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate MFA challenge token',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    # Extract the token from the credentials
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        # Ensure the token is an MFA challenge token
        if payload.get('token_type') != 'mfa_challenge':
            raise credentials_exception

        user_id = int(payload.get('sub'))
        if user_id is None:
            raise credentials_exception

    except jwt.PyJWTError:
        raise credentials_exception

    user = user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user


def require_permissions(*permissions: str):
    """Ensure the current user has all specified permissions."""

    def dependency(user=Depends(get_current_active_user)):
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Not authenticated',
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Inactive user',
            )

        # Flatten all user permissions into a set for easy checking
        user_permissions = {perm.name for role in user.roles for perm in role.permissions}
        missing_permissions = [perm for perm in permissions if perm not in user_permissions]

        # Deny access if any required permission is missing
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='You are not authorized to perform this action'
            )

        return True

    return dependency
