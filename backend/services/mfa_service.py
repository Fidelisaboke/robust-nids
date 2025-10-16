import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session

from core.config import settings
from core.dependencies import get_db_session, get_user_repository
from database.models import User
from database.repositories.user import UserRepository
from services.exceptions.mfa import (
    InvalidMFARecoveryTokenError,
    InvalidMFAVerificationCodeError,
    MFAAlreadyEnabledError,
    MFANotEnabledError,
)
from services.totp_service import TOTPService

logger = logging.getLogger(__name__)


class MFAService:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        totp_service: TOTPService = Depends(),
        user_repo: UserRepository = Depends(get_user_repository),
    ):
        self.session = session
        self.totp_service = totp_service
        self.user_repo = user_repo

    def setup_mfa(self, user: User) -> Dict[str, Any]:
        """Start MFA setup process"""
        if user.mfa_enabled:
            raise MFAAlreadyEnabledError()

        # Generate new secret
        secret = self.totp_service.generate_totp_secret()

        # Generate QR code
        totp_uri = self.totp_service.generate_totp_uri(secret, user.email)
        qr_code_b64 = self.totp_service.generate_qr_code(totp_uri)

        return {
            'secret': secret,  # Temporary - for display only
            'qr_code': f'data:image/png;base64,{qr_code_b64}',
            'totp_uri': totp_uri,
        }

    def verify_and_enable_mfa(self, user: User, verification_code: str, temp_secret: str) -> Dict[str, Any]:
        """Verify TOTP code and enable MFA"""
        if user.mfa_enabled:
            raise MFAAlreadyEnabledError()

        # Verify the code with the temporary secret
        if not self.totp_service.verify_totp_code(temp_secret, verification_code):
            raise InvalidMFAVerificationCodeError()

        # Generate backup codes for one-time display
        backup_codes = self.totp_service.generate_backup_codes()

        # Hash backup codes before storing
        hashed_codes = [self.totp_service.hash_backup_code(code) for code in backup_codes]

        # Update user with permanent secret and backup codes
        user.mfa_secret = temp_secret  # Store the verified secret
        user.mfa_backup_codes = hashed_codes
        user.mfa_enabled = True
        user.mfa_configured_at = datetime.now(timezone.utc)

        return {
            'backup_codes': backup_codes,
            'detail': 'MFA enabled successfully. Save your backup codes securely.',
        }

    def disable_mfa(self, user: User, verification_code: str) -> None:
        """Disable MFA after verification"""
        if not user.mfa_enabled:
            raise MFANotEnabledError()

        # Verify current TOTP code before disabling
        if not self.verify_mfa_code(user, verification_code):
            raise InvalidMFAVerificationCodeError()

        # Clear MFA data
        user.mfa_enabled = False
        user.mfa_secret = None
        user.mfa_backup_codes = None
        user.mfa_configured_at = None

    def admin_disable_mfa(self, user: User, performing_admin: User) -> None:
        """Disables MFA for a user, performed by an admin"""
        logger.info(
            f'ADMIN ACTION: MFA for user {user.email} (ID: {user.id}) '
            f'disabled by admin {performing_admin.email} (ID: {performing_admin.id})'
        )
        self.disable_mfa_for_user(user)

    def disable_mfa_for_user(self, user: User) -> None:
        """Disables MFA for a user object (used by admin or other flows)"""
        user.mfa_enabled = False
        user.mfa_secret = None
        user.mfa_backup_codes = None
        user.mfa_configured_at = None
        user.mfa_recovery_token = None
        user.mfa_recovery_token_expires = None

    def verify_mfa_code(self, user: User, code: str) -> bool:
        """Verify MFA code (TOTP or backup code)"""
        if not user.mfa_enabled:
            return True  # No MFA required

        # Try TOTP verification first
        if self.totp_service.verify_totp_code(user.mfa_secret, code):
            return True

        # Try backup code verification
        if user.mfa_backup_codes:
            is_valid, updated_codes = self.totp_service.verify_backup_code(code, user.mfa_backup_codes)
            if is_valid:
                user.mfa_backup_codes = updated_codes
                logger.warning(f'Backup code used for user_id={user.id}. {len(updated_codes)} codes left.')
                return True

        logger.warning(f'Failed MFA attempt for user_id={user.id}.')
        return False

    def complete_mfa_login(self, user: User, code: str):
        """Verifies MFA code and updates the user's last login time."""
        if not self.verify_mfa_code(user, code):
            # Use a custom exception instead of HTTPException
            raise InvalidMFAVerificationCodeError()

        user.last_login = datetime.now(timezone.utc)

    def generate_new_backup_codes(self, user: User, verification_code: str) -> List[str]:
        """Generate new backup codes (invalidates old ones)"""
        if not user.mfa_enabled:
            raise MFANotEnabledError()

        # Verify current TOTP code
        if not self.verify_mfa_code(user, verification_code):
            raise InvalidMFAVerificationCodeError()

        # Generate new backup codes
        new_backup_codes = self.totp_service.generate_backup_codes()
        hashed_codes = [self.totp_service.hash_backup_code(code) for code in new_backup_codes]
        user.mfa_backup_codes = hashed_codes

        return new_backup_codes

    @staticmethod
    def get_mfa_status(user: User) -> Dict[str, Any]:
        """Get current MFA status"""
        return {
            'mfa_enabled': user.mfa_enabled,
            'mfa_method': user.mfa_method,
            'mfa_configured_at': user.mfa_configured_at,
            'backup_codes_remaining': len(user.mfa_backup_codes) if user.mfa_backup_codes else 0,
        }

    def initiate_mfa_recovery(self, email: EmailStr):
        """Initiate MFA recovery process by generating a recovery token"""
        user = self.user_repo.get_by_email(email)

        if not user:
            return MFANotEnabledError()

        if not user.mfa_enabled:
            raise MFANotEnabledError()

        # Generate a secure recovery token
        recovery_token = secrets.token_urlsafe(32)

        # Hash token before storing it for security
        user.mfa_recovery_token = self.totp_service.hash_searchable_token(recovery_token)
        user.mfa_recovery_token_expires = datetime.now(timezone.utc) + timedelta(
            hours=settings.MFA_RECOVERY_TOKEN_EXPIRES_HOURS
        )

        # TODO: Send the recovery token to the user via email
        # send_mfa_recovery_email(user.email, recovery_token)

    def complete_mfa_recovery(self, recovery_token: str):
        """Disable MFA for a user after successful recovery."""

        hashed_token = self.totp_service.hash_searchable_token(recovery_token)
        user = self.user_repo.get_by_mfa_recovery_token(hashed_token)

        if not user:
            raise InvalidMFARecoveryTokenError()

        if not user.mfa_enabled:
            raise MFANotEnabledError()

        # Clear MFA data
        user.mfa_enabled = False
        user.mfa_secret = None
        user.mfa_backup_codes = None
        user.mfa_configured_at = None
        user.mfa_recovery_token = None
        user.mfa_recovery_token_expires = None

        # TODO: Notify user that MFA has been disabled
        # send_mfa_disabled_notification(user.email)
