"""
Authentication and Authorization API Endpoints.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from api.dependencies import get_current_active_user
from core.dependencies import get_user_repository
from core.security import (
    create_access_token,
    create_mfa_challenge_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from database.db import db
from database.models import User
from database.repositories.user import UserRepository
from schemas.auth import (
    ChangePasswordRequest,
    EmailVerificationRequest,
    EmailVerificationRequiredResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    MFAChallengeResponse,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from schemas.users import UserOut
from services.auth_service import AuthService, get_auth_service
from services.email_service import EmailService, get_email_service
from services.exceptions.mfa import InvalidMFAVerificationCodeError, MFAException
from services.token_service import URLTokenService, get_url_token_service

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)) -> LoginResponse:
    """User login endpoint.

    Args:
        request (LoginRequest): The login request containing email and password.
        auth_service (AuthService): The authentication service dependency.

    Raises:
        HTTPException: If authentication fails.

    Returns:
        LoginResponse: The login response which can be a token response,
                       MFA challenge response, or email verification required response.
    """
    user = auth_service.authenticate(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.email_verified:
        return EmailVerificationRequiredResponse(
            email_verified=False,
            email=user.email,
            detail="Email verification is required to log in.",
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


@router.post("/refresh", response_model=TokenResponse)
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
        detail="Refresh token is invalid or expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(request.refresh_token)
    if payload is None:
        raise refresh_token_exception

    # Check if token provided is a refresh token
    if payload.get("token_type") != "refresh":
        raise refresh_token_exception

    # Check token expiration
    exp = payload.get("exp")
    if exp is None or datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
        raise refresh_token_exception

    # Get user ID from token payload
    sub = payload.get("sub")
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
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

    new_access_token = create_access_token(user.id)
    return TokenResponse(access_token=new_access_token, refresh_token=request.refresh_token)


@router.get("/users/me", response_model=UserOut)
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


@router.post("/verify-email/request")
async def request_email_verification(
    request: EmailVerificationRequest,
    background_tasks: BackgroundTasks,
    user_repo: UserRepository = Depends(get_user_repository),
    token_service: URLTokenService = Depends(get_url_token_service),
    email_service: EmailService = Depends(get_email_service),
):
    """Request email verification for a user.

    Args:
        request (EmailVerificationRequest): The email verification request.
        background_tasks (BackgroundTasks): The background task manager.
        user_repo (UserRepository): The user repository. Defaults to Depends(get_user_repository).
        token_service (URLTokenService): The URL token service. Defaults to Depends(get_url_token_service).
        email_service (EmailService, optional): The email service. Defaults to Depends(get_email_service).

    Returns:
        dict: A success message upon successful request.
    """
    user = user_repo.get_by_email(request.email)

    if user and not user.email_verified:
        verification_token = token_service.create_email_verification_token(user.id)
        await email_service.send_verification_email(
            background_tasks=background_tasks,
            email=user.email,
            user_name=user.first_name or user.username,
            verification_token=verification_token,
        )

    return {"detail": "If the email exists, verification instructions have been sent."}


@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    token_service: URLTokenService = Depends(get_url_token_service),
):
    """Verify a user's email using a verification token.

    Args:
        request (VerifyEmailRequest): The email verification request containing the token.
        token_service (URLTokenService): The URL token service. Defaults to Depends(get_url_token_service).

    Raises:
        HTTPException: If the token is invalid or the user is not found.

    Returns:
        dict: A success message upon successful verification.
    """
    if not request.token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token is required",
        )

    try:
        if not token_service.mark_email_as_verified(request.token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )
        return {"detail": "Email verified successfully!"}
    except HTTPException as e:
        # Pass through expected HTTP errors
        raise e
    except Exception:
        # Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while verifying email",
        )


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    user_repo: UserRepository = Depends(get_user_repository),
    token_service: URLTokenService = Depends(get_url_token_service),
    email_service: EmailService = Depends(get_email_service),
):
    """
    Endpoint to initiate the password reset process.

    Args:
        request (ForgotPasswordRequest): The password reset request containing the user's email.
        background_tasks (BackgroundTasks): The background task manager.
        user_repo (UserRepository): The user repository. Defaults to Depends(get_user_repository).
        token_service (URLTokenService): The URL token service. Defaults to Depends(get_url_token_service).
        email_service (EmailService, optional): The email service. Defaults to Depends(get_email_service).

    Returns:
        dict: A success message upon successful verification.
    """
    user = user_repo.get_by_email(request.email)

    if user:
        reset_token = token_service.create_password_reset_token(user.id)
        await email_service.send_password_reset_email(
            background_tasks=background_tasks,
            email=user.email,
            user_name=user.first_name or user.username,
            reset_token=reset_token,
        )

    return {"detail": "If the email exists, password reset instructions have been sent."}


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Endpoint to reset the user's password using a valid reset token.

    Args:
        request (ResetPasswordRequest): The password reset request containing the token and new password.
        auth_service (AuthService): The authentication service dependency.

    Returns:
        dict: A success message upon successful verification.
    """

    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match.",
        )

    try:
        if not auth_service.reset_password(request.token, request.new_password, request.mfa_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token.",
            )
    except MFAException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA verification required for password reset.",
        )
    except InvalidMFAVerificationCodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA verification code.",
        )

    return {"detail": "Password reset successfully."}


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
    email_service: EmailService = Depends(get_email_service),
):
    """
    Endpoint to change the user's password.
    Intended for users already authenticated.

    Args:
        request (ChangePasswordRequest): The change password request containing the old and new passwords.
        auth_service (AuthService): The authentication service dependency.

    Returns:
        dict: A success message upon successful password change.
    """
    # Verify current password
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password.",
        )

    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match.",
        )

    # Update password
    auth_service.update_password(current_user, request.new_password)

    # Send password changed notification
    await email_service.send_password_change_notification_email(
        background_tasks=background_tasks,
        email=current_user.email,
        user_name=current_user.first_name or current_user.username
    )

    # Send password change notification email
    return {"detail": "Password changed successfully."}
