import base64
import io
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict
from sqlalchemy.orm import joinedload

import bcrypt
import pyotp
import qrcode

from database.db import db
from database.models import User
from utils.roles import SystemRoles


class IAuthService(ABC):
    """Authentication service interface."""

    @abstractmethod
    def authenticate(self, email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        pass

    @abstractmethod
    def verify_mfa(self, user: User, code: str) -> bool:
        pass


class AuthService(IAuthService):
    """Auth service class. Implements from Auth Service interface."""

    @staticmethod
    def create_user(email: str, password: str) -> int:
        with db.get_session() as session:
            existing_user = session.query(User).filter(User.email == email).first()

            if existing_user:
                raise ValueError("User already exists")

            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            new_user = User(
                email=email,
                password_hash=password_hash,
                mfa_secret=pyotp.random_base32(),
            )

            session.add(new_user)
            session.flush()
            return new_user.id

    def authenticate(self, email: str, password: str) -> Tuple[Optional[Dict], Optional[str]]:
        with db.get_session() as session:
            # Load the user with eager loading of roles
            user = (
                session.query(User).options(joinedload(User.roles)).filter(User.email == email, User.is_active).first()
            )

            if not user:
                return None, "Invalid credentials."

            # Check account lock
            if user.locked_until and user.locked_until > datetime.now():
                return None, "Account is locked."

            # Verify password
            if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
                user.failed_login_attempts = 0
                user.locked_until = None
                user.last_login = datetime.now()

                # Extract data before session closes
                user_data = {"id": user.id, "email": user.email, "roles": [role.name for role in user.roles]}
                session.commit()
                return user_data, None

            else:
                if SystemRoles.ADMIN.value not in [role.name for role in user.roles]:
                    user.failed_login_attempts += 1

                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.now() + timedelta(minutes=10)
                    return None, "Account locked due to too many failed attempts. Please try again in 10 minutes."

                session.commit()
                return None, "Invalid credentials."

    @staticmethod
    def generate_mfa_setup(user: User):
        """Generate MFA setup after enabling MFA."""
        if not user.mfa_secret:
            user.mfa_secret = pyotp.random_base32()

        totp = pyotp.TOTP(user.mfa_secret)
        uri = totp.provisioning_uri(name=user.email, issuer_name="NIDS Dashboard")

        # Generate QR code as base64 embedding in Streamlit
        qr = qrcode.make(uri)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode()
        return qr_b64

    def verify_mfa(self, user: User, token: str) -> bool:
        if not user.mfa_enabled:
            return True
        totp = pyotp.TOTP(user.mfa_secret)
        return totp.verify(token)

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        with db.get_session() as session:
            return session.query(User).options(joinedload(User.roles)).filter(User.id == user_id).first()

    @staticmethod
    def get_all_users():
        with db.get_session() as session:
            return session.query(User).order_by(User.created_at.desc()).all()
