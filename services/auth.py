import base64
import io
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, List

import bcrypt
import pyotp
import qrcode
from sqlalchemy.orm import joinedload

from core.config import DEFAULT_USER_PREFERENCES
from database.db import db
from database.models import User, UserSession
from utils.constants import SystemRoles, MFAMethod


class AuthService:
    """Auth service class. Implements from Auth Service interface."""

    @staticmethod
    def create_user(email: str, password: str, first_name: str, last_name: str, username: str, department: str) -> int:
        with db.get_session() as session:
            existing_user = session.query(User).filter((User.email == email) | (User.username == username)).first()

            if existing_user:
                raise ValueError("User already exists")

            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

            # Generate username if not provided
            if not username and email:
                username = email.split("@")[0]
                # Ensure uniqueness
                counter = 1
                base_username = username
                while session.query(User).filter(User.username == username).first():
                    username = f"{base_username}{counter}"
                    counter += 1

            new_user = User(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                department=department,
                password_hash=password_hash,
                mfa_secret=pyotp.random_base32(),
                preferences=AuthService.get_default_preferences(),
            )

            session.add(new_user)
            session.flush()
            return new_user.id

    @staticmethod
    def authenticate(email: str, password: str) -> Tuple[Optional[Dict], Optional[str]]:
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

                # Extract user data for session
                user_data = {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": user.phone,
                    "department": user.department,
                    "job_title": user.job_title,
                    "timezone": user.timezone,
                    "preferences": user.preferences or {},
                    "roles": [role.name for role in user.roles],
                    "mfa_enabled": user.mfa_enabled,
                    "mfa_method": user.mfa_method,
                    "profile_completed": user.profile_completed,
                }

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
    def get_default_preferences() -> Dict:
        """Return default user preferences"""
        return DEFAULT_USER_PREFERENCES

    @staticmethod
    def update_user_profile(user_id: int, update_data: Dict) -> bool:
        """Update user profile information"""
        with db.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            # Update basic profile fields
            profile_fields = ["first_name", "last_name", "phone", "department", "job_title", "timezone"]
            for field in profile_fields:
                if field in update_data:
                    setattr(user, field, update_data[field])

            # Update preferences if provided
            if "preferences" in update_data:
                user.preferences = {**user.preferences, **update_data["preferences"]}

            user.last_profile_update = datetime.now()

            # Check if profile is complete
            required_fields = ["first_name", "last_name", "email"]
            user.profile_completed = all(getattr(user, field) for field in required_fields)

            session.commit()
            return True

    @staticmethod
    def update_user_preferences(user_id: int, preferences: Dict) -> bool:
        """Update only user preferences"""
        with db.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            user.preferences = {**user.preferences, **preferences}
            session.commit()
            return True

    @staticmethod
    def generate_mfa_setup(user: User) -> dict:
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
        return {"qr_code": qr_b64, "secret": user.mfa_secret, "uri": uri, "backup_codes": user.mfa_backup_codes or []}

    def verify_totp(self, user_id: int, code: str) -> bool:
        """Verify TOTP token for a user"""
        with db.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user or not user.mfa_enabled:
                return True  # MFA not enabled, allow access

            # Check backup codes first
            if user.mfa_backup_codes and code in user.mfa_backup_codes:
                # Remove used backup code
                self._remove_backup_code(session, user, code)
                return True

            # Verify TOTP
            if user.mfa_secret:
                totp = pyotp.TOTP(user.mfa_secret)
                return totp.verify(code, valid_window=1)  # Allow 30-second window

            return False

    @staticmethod
    def _remove_backup_code(session, user: User, code: str) -> None:
        """Remove a used backup code"""
        if user.mfa_backup_codes:
            user.mfa_backup_codes = [c for c in user.mfa_backup_codes if c != code]
            session.commit()

    @staticmethod
    def enable_mfa(secret: str, user_id: int, method: str = MFAMethod.TOTP.value) -> dict:
        """Enable MFA for a user and return setup data"""
        with db.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "User not found."}

            user.mfa_secret = secret
            user.mfa_enabled = True
            user.mfa_method = method
            user.mfa_configured_at = datetime.now()

            # Generate backup codes
            backup_codes = [pyotp.random_base32()[:8].upper() for _ in range(10)]

            # Hash backup codes for storage
            hashed_backup_codes = [bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode() for code in backup_codes]
            user.mfa_backup_codes = hashed_backup_codes

            session.commit()
            return {"success": True, "message": "MFA enabled successfully.", "backup_codes": backup_codes}

    @staticmethod
    def disable_mfa(user_id: int) -> bool:
        """Disable MFA for a user"""
        with db.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            user.mfa_enabled = False
            user.mfa_method = None
            user.mfa_secret = None
            user.mfa_backup_codes = None
            user.mfa_configured_at = None

            session.commit()
            return True

    @staticmethod
    def create_user_session(
        user_id: int, session_id: str, device_info: str, ip_address: str, user_agent: str, expires_after: int = 3600
    ) -> bool:
        """Create a new user session"""
        with db.get_session() as session:
            new_session = UserSession(
                id=session_id,
                user_id=user_id,
                device_info=device_info,
                ip_address=ip_address,
                user_agent=user_agent,
                login_time=datetime.now(),
                last_activity=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=expires_after),
                is_active=True,
            )
            session.add(new_session)
            session.commit()
            return True

    @staticmethod
    def get_user_sessions(user_id: int) -> List[Dict]:
        """Get all active sessions for a user"""
        with db.get_session() as session:
            sessions = (
                session.query(UserSession)
                .filter(UserSession.user_id == user_id, UserSession.is_active)
                .order_by(UserSession.last_activity.desc())
                .all()
            )

            return [
                {
                    "id": s.id,
                    "device_info": s.device_info,
                    "ip_address": s.ip_address,
                    "login_time": s.login_time,
                    "last_activity": s.last_activity,
                    "is_current": False,  # Will be set by caller
                }
                for s in sessions
            ]

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        with db.get_session() as session:
            return session.query(User).options(joinedload(User.roles)).filter(User.id == user_id).first()

    @staticmethod
    def get_user_profile(user_id: int) -> Optional[Dict]:
        """Get complete user profile data"""
        with db.get_session() as session:
            user = session.query(User).options(joinedload(User.roles)).filter(User.id == user_id).first()

        if not user:
            return None

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "department": user.department,
            "job_title": user.job_title,
            "timezone": user.timezone,
            "preferences": user.preferences or {},
            "roles": [role.name for role in user.roles],
            "mfa_enabled": user.mfa_enabled,
            "mfa_method": user.mfa_method,
            "profile_completed": user.profile_completed,
            "last_login": user.last_login,
            "created_at": user.created_at,
        }

    @staticmethod
    def get_all_users():
        with db.get_session() as session:
            return session.query(User).options(joinedload(User.roles)).order_by(User.created_at.desc()).all()

    @staticmethod
    def authenticate_with_backup_code(email: str, backup_code: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Authenticate user using backup code"""
        with db.get_session() as session:
            user = session.query(User).filter(User.email == email, User.is_active).first()

            if not user:
                return None, "Invalid credentials"

            if not user.mfa_enabled:
                return None, "MFA not enabled for this account"

            if not user.mfa_backup_codes:
                return None, "No backup codes available"

            # Check each hashed backup code
            valid_code_index = -1
            for i, hashed_code in enumerate(user.mfa_backup_codes):
                try:
                    if bcrypt.checkpw(backup_code.upper().encode(), hashed_code.encode()):
                        valid_code_index = i
                        break
                except Exception:
                    continue  # Skip invalid hashes

            if valid_code_index != -1:
                # Remove the used backup code
                user.mfa_backup_codes.pop(valid_code_index)

                # Update user session data
                user.last_login = datetime.now()
                user.failed_login_attempts = 0

                user_data = {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "roles": [role.name for role in user.roles],
                    "mfa_enabled": user.mfa_enabled,
                    "used_backup_code": True,  # Flag for post-login actions
                }

                session.commit()
                return user_data, None
            else:
                return None, "Invalid backup code"

    @staticmethod
    def generate_new_backup_codes(user_id: int) -> Dict:
        """Generate new backup codes (replaces old ones)"""
        with db.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "User not found"}

            new_codes_plain = [pyotp.random_base32()[:8].upper() for _ in range(10)]
            new_codes_hashed = [bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode() for code in new_codes_plain]
            user.mfa_backup_codes = new_codes_hashed

            session.commit()
            return {"success": True, "message": "New backup codes generated", "backup_codes": new_codes_plain}
