from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr

from backend.core.config import settings
from backend.database.db import db
from backend.database.models import User
from backend.database.repositories.user import UserRepository

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/token')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version."""
    try:
        # Convert plain password to bytes
        password_bytes = plain_password.encode('utf-8')

        # Handle hashed password that might be bytes or str
        if isinstance(hashed_password, str):
            hashed_bytes = hashed_password.encode('utf-8')
        else:
            hashed_bytes = hashed_password

        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except (TypeError, ValueError):
        return False


def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def authenticate_user(email: str | EmailStr, password: str):
    """Authenticate user by email and password."""
    with db.get_session() as session:
        user = session.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


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
    exp = payload.get('exp')
    if exp is None:
        return True
    expiration = datetime.fromtimestamp(exp, tz=timezone.utc)
    return expiration < datetime.now(timezone.utc)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Retrieve the current user based on the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = int(payload.get('sub'))
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    with db.get_session() as session:
        user_repo = UserRepository(session)
        user = user_repo.get_by_id(user_id)
        if user is None:
            raise credentials_exception
        return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user
