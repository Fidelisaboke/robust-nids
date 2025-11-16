from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version."""
    try:
        # Convert plain password to bytes
        password_bytes = plain_password.encode("utf-8")

        # Handle hashed password that might be bytes or str
        if isinstance(hashed_password, str):
            hashed_bytes = hashed_password.encode("utf-8")
        else:
            hashed_bytes = hashed_password

        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except (TypeError, ValueError):
        return False


def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def _create_token(user_id: int, minutes: int, token_type: str) -> str:
    """Create a JWT token with the given user ID, expiration time, and token type."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {"sub": str(user_id), "exp": expire, "token_type": token_type}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: int) -> str:
    """Create a JWT access token for the given user ID."""
    return _create_token(user_id, settings.ACCESS_TOKEN_EXPIRE_MINUTES, "access")


def create_refresh_token(user_id: int) -> str:
    """Create a JWT refresh token for the given user ID."""
    return _create_token(user_id, settings.REFRESH_TOKEN_EXPIRE_MINUTES, "refresh")


def create_mfa_challenge_token(user_id: int) -> str:
    """Create a JWT token for MFA challenge for the given user ID."""
    return _create_token(user_id, settings.MFA_CHALLENGE_TOKEN_EXPIRE_MINUTES, "mfa_challenge")


def decode_token(token: str):
    """Decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def is_token_expired(token: str) -> bool:
    """Check if a JWT token is expired."""
    payload = decode_token(token)
    if payload is None:
        return True
    exp = payload.get("exp")
    if exp is None:
        return True
    expiration = datetime.fromtimestamp(exp, tz=timezone.utc)
    return expiration < datetime.now(timezone.utc)
