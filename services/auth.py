import base64
import io
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import bcrypt
import pyotp
import qrcode
from sqlalchemy.orm import joinedload

from core.config import DEFAULT_USER_PREFERENCES
from core.singleton import SingletonMeta
from database.models import User, UserSession
from utils.constants import MFAMethod, SystemRoles

logger = logging.getLogger("auth")
logger.setLevel(logging.INFO)


class AuthService(metaclass=SingletonMeta):
    """
    Auth service class. Handles authentication, MFA, and user session management.
    All methods are instance methods unless stateless utility.
    """

    def __init__(self, db_session_factory: Any):
        """
        Args:
            db_session_factory: Callable that returns a SQLAlchemy session context manager.
        """
        self.db_session_factory = db_session_factory

    def create_user(
        self, email: str, password: str, first_name: str, last_name: str, username: str, department: str
    ) -> int:
        """Create a new user in the database."""
        if not email or not password:
            raise ValueError("Email and password are required.")
        with self.db_session_factory() as session:
            existing_user = session.query(User).filter((User.email == email) | (User.username == username)).first()
            if existing_user:
                logger.warning(f"Attempt to create duplicate user: {email} / {username}")
                raise ValueError("User already exists")

            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

            # Generate username if not provided
            if not username and email:
                username = email.split("@")[0]
                counter = 1
                base_username = username
                while session.query(User).filter(User.username == username).first():
                    username = f"{base_username}{counter}"
                    counter += 1

            # Create new user
            new_user = User(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                department=department,
                password_hash=password_hash,
                mfa_secret=pyotp.random_base32(),
                preferences=self.get_default_preferences(),
            )
            session.add(new_user)
            session.flush()
            logger.info(f"User created: {email} ({new_user.id})")
            return new_user.id

    def authenticate(
        self,
        email: str,
        password: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> dict:
        """
        Authenticate user by email and password, create session on success.
        Returns a dict: {"user": user_data or None, "error": error_message or None, "session_id": session_id or None}
        """
        import uuid

        if not email or not password:
            return {"user": None, "error": "Email and password required.", "session_id": None}
        with self.db_session_factory() as session:
            user = (
                session.query(User).options(joinedload(User.roles)).filter(User.email == email, User.is_active).first()
            )
            if not user:
                logger.warning(f"Failed login attempt for {email}: user not found or inactive.")
                return {"user": None, "error": "Invalid credentials.", "session_id": None}
            if user.locked_until and user.locked_until > datetime.now():
                logger.warning(f"Login attempt for locked account {email}.")
                return {"user": None, "error": "Account is locked.", "session_id": None}
            if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
                user.failed_login_attempts = 0
                user.locked_until = None
                user.last_login = datetime.now()
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
                # Create session
                session_id = str(uuid.uuid4())
                new_session = UserSession(
                    id=session_id,
                    user_id=user.id,
                    device_info=device_info or "Unknown",
                    ip_address=ip_address or "Unknown",
                    user_agent=user_agent or "Unknown",
                    login_time=datetime.now(),
                    last_activity=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=1),
                    is_active=True,
                )
                session.add(new_session)
                session.commit()
                logger.info(f"Successful login for {email}. Session {session_id} created.")
                return {"user": user_data, "error": None, "session_id": session_id}
            else:
                if SystemRoles.ADMIN.value not in [role.name for role in user.roles]:
                    user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.now() + timedelta(minutes=10)
                    session.commit()
                    logger.warning(f"Account locked due to failed attempts: {email}")
                    return {
                        "user": None,
                        "error": "Account locked due to too many failed attempts. Please try again in 10 minutes.",
                        "session_id": None,
                    }
                session.commit()
                logger.warning(f"Failed login for {email}: invalid password.")
                return {"user": None, "error": "Invalid credentials.", "session_id": None}

    def logout_user(self, user_id: int, session_id: str) -> bool:
        """
        Log out a user by marking the session inactive and updating last_activity/logout_time.
        """
        if not user_id or not session_id:
            raise ValueError("user_id and session_id are required.")
        with self.db_session_factory() as session:
            user_session = (
                session.query(UserSession)
                .filter(UserSession.id == session_id, UserSession.user_id == user_id, UserSession.is_active)
                .first()
            )
            if not user_session:
                logger.warning(f"Logout failed: session {session_id} for user {user_id} not found or already inactive.")
                return False
            user_session.is_active = False
            user_session.last_activity = datetime.now()
            user_session.expires_at = datetime.now()
            session.commit()
            logger.info(f"User {user_id} logged out from session {session_id}.")
            return True

    def refresh_session(self, session_id: str, extend_seconds: int = 3600) -> bool:
        """
        Update last_activity and extend expires_at if session is still valid.
        """
        if not session_id:
            raise ValueError("session_id is required.")
        with self.db_session_factory() as session:
            user_session = (
                session.query(UserSession).filter(UserSession.id == session_id, UserSession.is_active).first()
            )
            if not user_session:
                logger.warning(f"Session refresh failed: session {session_id} not found or inactive.")
                return False
            now = datetime.now()
            if user_session.expires_at < now:
                user_session.is_active = False
                session.commit()
                logger.info(f"Session {session_id} expired and marked inactive during refresh.")
                return False
            user_session.last_activity = now
            user_session.expires_at = now + timedelta(seconds=extend_seconds)
            session.commit()
            logger.info(f"Session {session_id} refreshed and expiry extended.")
            return True

    def invalidate_all_sessions(self, user_id: int) -> int:
        """
        Log out user from all devices (set all sessions inactive).
        Returns number of sessions invalidated.
        """
        if not user_id:
            raise ValueError("user_id is required.")
        with self.db_session_factory() as session:
            sessions = session.query(UserSession).filter(UserSession.user_id == user_id, UserSession.is_active).all()
            count = 0
            for s in sessions:
                s.is_active = False
                s.expires_at = datetime.now()
                s.last_activity = datetime.now()
                count += 1
            session.commit()
            logger.info(f"User {user_id} forcibly logged out from {count} sessions.")
            return count

    def get_default_preferences(self) -> Dict:
        """Return default user preferences."""
        return DEFAULT_USER_PREFERENCES

    def update_user_profile(self, user_id: int, update_data: Dict) -> bool:
        """Update user profile information."""
        if not user_id:
            raise ValueError("user_id is required.")

        with self.db_session_factory() as session:
            # Check if user exists
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"Profile update failed: user {user_id} not found.")
                return False

            # Update profile fields
            profile_fields = ["first_name", "last_name", "phone", "department", "job_title", "timezone"]
            for field in profile_fields:
                if field in update_data:
                    setattr(user, field, update_data[field])

            # Update preferences if provided
            if "preferences" in update_data:
                if user.preferences is None:
                    user.preferences = {}
                user.preferences = {**user.preferences, **update_data["preferences"]}

            # Update profile completion status
            user.last_profile_update = datetime.now()
            required_fields = ["first_name", "last_name", "email"]
            user.profile_completed = all(getattr(user, field) for field in required_fields)
            session.commit()
            logger.info(f"Profile updated for user {user_id}.")
            return True

    def update_user_preferences(self, user_id: int, preferences: Dict) -> bool:
        """Update only user preferences."""
        if not user_id:
            raise ValueError("user_id is required.")
        with self.db_session_factory() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"Preferences update failed: user {user_id} not found.")
                return False

            # Update preferences
            if user.preferences is None:
                user.preferences = {}
            user.preferences = {**user.preferences, **preferences}
            session.commit()
            logger.info(f"Preferences updated for user {user_id}.")
            return True

    def generate_mfa_setup(self, user: User) -> dict:
        """Generate MFA setup after enabling MFA."""
        if not user.mfa_secret:
            user.mfa_secret = pyotp.random_base32()

        # Generate QR code
        totp = pyotp.TOTP(user.mfa_secret)
        uri = totp.provisioning_uri(name=user.email, issuer_name="NIDS Dashboard")
        qr = qrcode.make(uri)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode()
        logger.info(f"MFA setup generated for user {user.id}.")
        buf.close()
        return {"qr_code": qr_b64, "secret": user.mfa_secret, "uri": uri, "backup_codes": user.mfa_backup_codes or []}

    def verify_totp(self, user_id: int, code: str) -> bool:
        """Verify TOTP token or backup code for a user."""
        if not user_id:
            raise ValueError("user_id is required.")
        with self.db_session_factory() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user or not user.mfa_enabled:
                logger.info(f"TOTP verification bypassed for user {user_id} (MFA not enabled).")
                return True

            # Check backup codes first (atomic removal)
            if user.mfa_backup_codes:
                for i, hashed_code in enumerate(user.mfa_backup_codes):
                    try:
                        if bcrypt.checkpw(code.upper().encode(), hashed_code.encode()):
                            user.mfa_backup_codes.pop(i)
                            session.commit()
                            logger.info(f"Backup code used for user {user_id}.")
                            return True
                    except Exception:
                        continue

            # Verify TOTP
            if user.mfa_secret:
                totp = pyotp.TOTP(user.mfa_secret)
                if totp.verify(code, valid_window=1):
                    logger.info(f"TOTP verified for user {user_id}.")
                    return True
                else:
                    logger.warning(f"Failed TOTP verification for user {user_id}.")
                    return False

            # TOTP not set up properly
            logger.warning(f"Failed TOTP/backup code verification for user {user_id}.")
            return False

    def enable_mfa(self, secret: str, user_id: int, method: str = MFAMethod.TOTP.value) -> dict:
        """Enable MFA for a user and return setup data."""
        if not user_id:
            raise ValueError("user_id is required.")
        with self.db_session_factory() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"Enable MFA failed: user {user_id} not found.")
                return {"success": False, "message": "User not found."}

            # Enable MFA
            user.mfa_secret = secret
            user.mfa_enabled = True
            user.mfa_method = method
            user.mfa_configured_at = datetime.now()

            # Generate backup codes
            backup_codes = [pyotp.random_base32()[:8].upper() for _ in range(10)]
            hashed_backup_codes = [bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode() for code in backup_codes]
            user.mfa_backup_codes = hashed_backup_codes

            # Commit changes
            session.commit()
            logger.info(f"MFA enabled for user {user_id}.")
            return {"success": True, "message": "MFA enabled successfully.", "backup_codes": backup_codes}

    def disable_mfa(self, user_id: int) -> bool:
        """Disable MFA for a user."""
        if not user_id:
            raise ValueError("user_id is required.")
        with self.db_session_factory() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"Disable MFA failed: user {user_id} not found.")
                return False

            # Reset MFA fields
            user.mfa_enabled = False
            user.mfa_method = None
            user.mfa_secret = None
            user.mfa_backup_codes = None
            user.mfa_configured_at = None
            session.commit()
            logger.info(f"MFA disabled for user {user_id}.")
            return True

    def create_user_session(
        self,
        user_id: int,
        session_id: str,
        device_info: str,
        ip_address: str,
        user_agent: str,
        expires_after: int = 3600,
    ) -> bool:
        """Create a new user session."""
        if not user_id or not session_id:
            raise ValueError("user_id and session_id are required.")
        with self.db_session_factory() as session:
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
            logger.info(f"User session created for user {user_id} (session {session_id}).")
            return True

    def get_user_sessions(self, user_id: int, current_session_id: Optional[str] = None) -> List[Dict]:
        """
        Get all active sessions for a user, flagging current session if provided.
        Expired sessions are marked inactive and not returned.
        """
        if not user_id:
            raise ValueError("user_id is required.")
        with self.db_session_factory() as session:
            now = datetime.now()
            sessions = (
                session.query(UserSession)
                .filter(UserSession.user_id == user_id, UserSession.is_active)
                .order_by(UserSession.last_activity.desc())
                .all()
            )
            result = []
            for s in sessions:
                if s.expires_at < now:
                    s.is_active = False
                    session.commit()
                    logger.info(f"Session {s.id} expired and marked inactive during fetch.")
                    continue
                result.append(
                    {
                        "id": s.id,
                        "device_info": s.device_info,
                        "ip_address": s.ip_address,
                        "login_time": s.login_time,
                        "last_activity": s.last_activity,
                        "is_current": (current_session_id == s.id) if current_session_id else False,
                    }
                )
            return result

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        if not user_id:
            raise ValueError("user_id is required.")
        with self.db_session_factory() as session:
            return session.query(User).options(joinedload(User.roles)).filter(User.id == user_id).first()

    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get complete user profile data."""
        if not user_id:
            raise ValueError("user_id is required.")
        with self.db_session_factory() as session:
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

    def get_all_users(self) -> List[User]:
        """Get all users."""
        with self.db_session_factory() as session:
            return session.query(User).options(joinedload(User.roles)).order_by(User.created_at.desc()).all()

    def authenticate_with_backup_code(self, email: str, backup_code: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Authenticate user using backup code."""
        if not email or not backup_code:
            return None, "Email and backup code required."
        with self.db_session_factory() as session:
            user = session.query(User).filter(User.email == email, User.is_active).first()
            if not user:
                logger.warning(f"Backup code login failed for {email}: user not found or inactive.")
                return None, "Invalid credentials"
            if not user.mfa_enabled:
                return None, "MFA not enabled for this account"
            if not user.mfa_backup_codes:
                return None, "No backup codes available"
            valid_code_index = -1
            for i, hashed_code in enumerate(user.mfa_backup_codes):
                try:
                    if bcrypt.checkpw(backup_code.upper().encode(), hashed_code.encode()):
                        valid_code_index = i
                        break
                except Exception:
                    continue
            if valid_code_index != -1:
                user.mfa_backup_codes.pop(valid_code_index)
                user.last_login = datetime.now()
                user.failed_login_attempts = 0
                user_data = {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "roles": [role.name for role in user.roles],
                    "mfa_enabled": user.mfa_enabled,
                    "used_backup_code": True,
                }
                session.commit()
                logger.info(f"Backup code login for {email}.")
                return user_data, None
            else:
                logger.warning(f"Invalid backup code attempt for {email}.")
                return None, "Invalid backup code"

    def generate_new_backup_codes(self, user_id: int) -> Dict:
        """Generate new backup codes (replaces old ones)."""
        if not user_id:
            raise ValueError("user_id is required.")
        with self.db_session_factory() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"Generate backup codes failed: user {user_id} not found.")
                return {"success": False, "message": "User not found"}
            new_codes_plain = [pyotp.random_base32()[:8].upper() for _ in range(10)]
            new_codes_hashed = [bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode() for code in new_codes_plain]
            user.mfa_backup_codes = new_codes_hashed
            session.commit()
            logger.info(f"New backup codes generated for user {user_id}.")
            return {"success": True, "message": "New backup codes generated", "backup_codes": new_codes_plain}
