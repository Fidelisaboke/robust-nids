import json

from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter

from backend.api.schemas.auth import TokenResponse
from backend.api.schemas.mfa import MFAEnablePayload, MFAVerifyPayload
from backend.database.db import db
from backend.database.models import User
from backend.services.auth_service import create_access_token, create_refresh_token, get_current_active_user
from backend.services.mfa_service import MFAService
from backend.services.totp_service import totp_service


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

router = APIRouter(prefix="/api/v1/auth/mfa", tags=["mfa"])
limiter_by_user = Limiter(key_func=get_key_from_request_state)

@router.post("/setup")
def setup_mfa(current_user: User = Depends(get_current_active_user)):
    """Begin MFA setup for logged-in user."""
    with db.get_session() as session:
        service = MFAService(session, totp_service=totp_service)
        return service.setup_mfa(current_user)

@router.post("/enable")
def enable_mfa(payload: MFAEnablePayload, current_user: User = Depends(get_current_active_user)):
    """Verify code and enable MFA."""
    with db.get_session() as session:
        # Attach user to session
        current_user = session.merge(current_user)
        service = MFAService(session, totp_service=totp_service)
        return service.verify_and_enable_mfa(current_user, payload.verification_code, payload.temp_secret)

@router.post("/verify")
@limiter_by_user.limit("5/minute")
def verify_mfa(request: Request, payload: MFAVerifyPayload):
    """Verify TOTP code during login."""
    with db.get_session() as session:
        service = MFAService(session, totp_service=totp_service)
        user = session.query(User).filter(User.id == payload.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not service.verify_mfa_code(user, payload.code):
            raise HTTPException(status_code=400, detail="Invalid or expired code")

        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        return TokenResponse(access_token=access, refresh_token=refresh)
