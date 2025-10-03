"""
Authentication and Authorization API Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from api.schemas.auth import LoginRequest, TokenResponse, RefreshRequest
from api.schemas.users import UserOut
from api.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_active_user,
    is_token_expired,
)
from database.models import User
from database.db import db
from datetime import datetime, timezone

router = APIRouter(prefix='/api/v1/auth', tags=['auth'])


@router.post('/login', response_model=TokenResponse)
def login(request: LoginRequest) -> TokenResponse:
    """User login endpoint.

    Args:
        request (LoginRequest): The login request containing email and password.

    Raises:
        HTTPException: If authentication fails.

    Returns:
        TokenResponse: The token response containing access and refresh tokens.
    """
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token = create_access_token(data={'sub': str(user.id)})
    refresh_token = create_refresh_token(data={'sub': str(user.id)})

    # Update last login time
    with db.get_session() as session:
        user_in_db = session.query(User).filter(User.id == user.id).first()
        if user_in_db:
            user_in_db.last_login = datetime.now(timezone.utc)
            session.add(user_in_db)
            session.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post('/token', response_model=TokenResponse)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2-compatible token login, accepts form data from Swagger UI.\n
    Note: In OAuth2PasswordRequestForm, 'username' field is used for email.

    Args:
        form_data (OAuth2PasswordRequestForm): The OAuth2 form containing username & password.

    Returns:
        TokenResponse: Access token and refresh token.
    """
    # In your case, username will be the email
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token = create_access_token(data={'sub': str(user.id)})
    refresh_token = create_refresh_token(data={'sub': str(user.id)})

    # Update last login time
    with db.get_session() as session:
        user_in_db = session.query(User).filter(User.id == user.id).first()
        if user_in_db:
            user_in_db.last_login = datetime.now(timezone.utc)
            session.add(user_in_db)
            session.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type='bearer')


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
        detail='Could not validate refresh token',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    payload = decode_token(request.refresh_token)
    if payload is None:
        raise refresh_token_exception

    # Check token expiration
    if is_token_expired(request.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token has expired',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # Get user ID from token payload
    user_id = int(payload.get('sub'))
    if user_id is None:
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

    new_access_token = create_access_token(data={'sub': str(user_id)})
    return TokenResponse(access_token=new_access_token, refresh_token=request.refresh_token)


@router.get('/users/me', response_model=UserOut)
async def read_profile(
    current_user: User = Depends(get_current_active_user),
) -> UserOut:
    """Get the current user's profile.

    Args:
        current_user (User): The currently authenticated user.

    Returns:
        UserOut: The current user's profile.
    """
    return current_user
