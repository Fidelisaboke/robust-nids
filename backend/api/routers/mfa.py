import json

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter

from api.dependencies import get_current_active_user, get_user_from_mfa_challenge_token
from core.security import (
    create_access_token,
    create_refresh_token,
)
from database.models import User
from schemas.auth import TokenResponse
from schemas.mfa import (
    MFADisableResponse,
    MFAEnablePayload,
    MFAEnableResponse,
    MFARecoveryCompleteRequest,
    MFARecoveryCompleteResponse,
    MFARecoveryInitiateRequest,
    MFARecoveryInitiateResponse,
    MFASetupResponse,
    MFAVerifyPayload,
)
from services.mfa_service import MFAService


def get_key_from_request_state(request: Request) -> str:
    """
    Reads the user_id from the request body, which was preloaded
    by the middleware, to create a unique rate-limiting key.
    """
    try:
        # The request body is already loaded into request.state by the middleware
        body = json.loads(request.state.body)
        user_id = body.get("user_id", "unknown_user")
        return f"mfa-verify-{user_id}"
    except (json.JSONDecodeError, AttributeError):
        # A fallback key in case the body is empty or not valid JSON
        return str(request.client.host)


router = APIRouter(prefix="/api/v1/auth/mfa", tags=["Multi-Factor Authentication"])
limiter_by_user = Limiter(key_func=get_key_from_request_state)


@router.get("/setup", response_model=MFASetupResponse)
def setup_mfa(current_user: User = Depends(get_current_active_user), mfa_service: MFAService = Depends()):
    """Begin MFA setup for logged-in user."""
    return mfa_service.setup_mfa(current_user)


@router.post("/enable", response_model=MFAEnableResponse)
def enable_mfa(
    payload: MFAEnablePayload,
    current_user: User = Depends(get_current_active_user),
    mfa_service: MFAService = Depends(),
):
    """Verify code and enable MFA."""
    return mfa_service.verify_and_enable_mfa(current_user, payload.verification_code, payload.temp_secret)


@router.post("/verify")
@limiter_by_user.limit("5/minute")
def verify_mfa(
    request: Request,
    payload: MFAVerifyPayload,
    user: User = Depends(get_user_from_mfa_challenge_token),
    mfa_service: MFAService = Depends(),
):
    """Verify TOTP code during login (Step 2 of two-factor login)."""
    mfa_service.complete_mfa_login(user, payload.code)
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/disable", response_model=MFADisableResponse)
def disable_mfa(
    payload: MFAVerifyPayload,
    current_user: User = Depends(get_current_active_user),
    mfa_service: MFAService = Depends(),
):
    """Disable MFA for the current user after verifying their TOTP code."""
    mfa_service.disable_mfa(current_user, payload.code)

    return {"detail": "MFA has been disabled successfully."}


@router.post("/recovery/initiate", response_model=MFARecoveryInitiateResponse)
@limiter_by_user.limit("5/hour")
def initiate_mfa_recovery(
    request: Request, payload: MFARecoveryInitiateRequest, mfa_service: MFAService = Depends()
):
    """Initiate MFA recovery process by sending a recovery email."""
    mfa_service.initiate_mfa_recovery(payload.email)

    return {"detail": "If the email is registered, a recovery link has been sent."}


@router.post("/recovery/complete", response_model=MFARecoveryCompleteResponse)
def complete_mfa_recovery(request: MFARecoveryCompleteRequest, mfa_service: MFAService = Depends()):
    """Complete MFA recovery using a valid recovery token."""
    mfa_service.complete_mfa_recovery(request.mfa_recovery_token)

    return {"detail": "MFA has been disabled. Please log in and set up MFA again if desired."}
