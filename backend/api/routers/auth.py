"""
Authentication and Authorization API Endpoints.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.dependencies import get_current_active_user
from backend.core.security import (
    create_access_token,
    create_mfa_challenge_token,
    create_refresh_token,
    decode_token,
)
from backend.database.db import db
from backend.database.models import User
from backend.schemas.auth import LoginRequest, MFAChallengeResponse, RefreshRequest, TokenResponse
from backend.schemas.users import UserOut
from backend.services.auth_service import AuthService

router = APIRouter(prefix='/api/v1/auth', tags=['Authentication'])


@router.post('/login', response_model=TokenResponse | MFAChallengeResponse)
def login(
    request: LoginRequest,
    auth_service: AuthService = Depends()
) -> TokenResponse | MFAChallengeResponse:
    """User login endpoint.

    Args:
        request (LoginRequest): The login request containing email and password.
        auth_service (AuthService): The authentication service dependency.

    Raises:
        HTTPException: If authentication fails.

    Returns:
        TokenResponse: The token response containing access and refresh tokens.
    """
    user = auth_service.authenticate(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    if user.mfa_enabled:
        challenge_token = create_mfa_challenge_token(user.id)
        return MFAChallengeResponse(mfa_required=True, mfa_challenge_token=challenge_token)

    new_access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)

    # Update last login time
    with db.get_session() as session:
        user_in_session = session.merge(user)
        user_in_session.last_login = datetime.now(timezone.utc)
        session.commit()

    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)


@router.post('/refresh', response_model=TokenResponse)
def refresh_token(request: RefreshRequest) -> TokenResponse:
    """Refresh access token using refresh token.

    Args:
        request (RefreshRequest): The request containing the refresh token.

    Raises:
            HTTPException: If the refresh token is invalid, expired, or the user is not found or inactive.

    Returns:
            TokenResponse: The new access token and the same refresh token.
    """
    refresh_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Refresh token is invalid or expired',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    payload = decode_token(request.refresh_token)
    if payload is None:
        raise refresh_token_exception

    # Check if token provided is a refresh token
    if payload.get('token_type') != 'refresh':
        raise refresh_token_exception

    # Check token expiration
    exp = payload.get('exp')
    if exp is None or datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
        raise refresh_token_exception

    # Get user ID from token payload
    sub = payload.get('sub')
    if sub is None:
        raise refresh_token_exception
    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise refresh_token_exception

    # Check if the user still exists and is active
    with db.get_session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User not found',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='User is inactive',
                headers={'WWW-Authenticate': 'Bearer'},
            )

    new_access_token = create_access_token(user.id)
    return TokenResponse(access_token=new_access_token, refresh_token=request.refresh_token)


@router.get('/users/me', response_model=UserOut)
async def read_profile(
        current_user: UserOut = Depends(get_current_active_user),
) -> UserOut:
    """Get the current user's profile.

    Args:
        current_user (UserOut): The currently authenticated user.

    Returns:
        UserOut: The current user's profile.
    """
    return current_user
