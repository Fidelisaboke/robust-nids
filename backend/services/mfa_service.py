from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.database.models import User
from backend.services.totp_service import TOTPService


class MFAService:
    def __init__(self, session: Session, totp_service: TOTPService):
        self.db = session
        self.totp_service = totp_service

    def setup_mfa(self, user: User) -> Dict[str, Any]:
        """Start MFA setup process"""
        if user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='MFA is already enabled for this user.'
            )

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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='MFA already enabled for user'
            )

        # Verify the code with the temporary secret
        if not self.totp_service.verify_totp_code(temp_secret, verification_code):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid TOTP code')

        # Generate backup codes for one-time display
        backup_codes = self.totp_service.generate_backup_codes()

        # Hash backup codes before storing
        hashed_codes = [self.totp_service.hash_backup_code(code) for code in backup_codes]

        # Update user with permanent secret and backup codes
        user.mfa_secret = temp_secret  # Store the verified secret
        user.mfa_backup_codes = hashed_codes
        user.mfa_enabled = True
        user.mfa_configured_at = datetime.now(timezone.utc)

        self.db.commit()

        return {
            'backup_codes': backup_codes,
            'message': 'MFA enabled successfully. Save your backup codes securely.',
        }

    def disable_mfa(self, user: User, verification_code: str) -> None:
        """Disable MFA after verification"""
        if not user.mfa_enabled:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='MFA not enabled for user')

        # Verify current TOTP code before disabling
        if not self.verify_mfa_code(user, verification_code):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid verification code')

        # Clear MFA data
        user.mfa_enabled = False
        user.mfa_secret = None
        user.mfa_backup_codes = None
        user.mfa_configured_at = None

        self.db.commit()

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
                return True

        return False

    def generate_new_backup_codes(self, user: User, verification_code: str) -> List[str]:
        """Generate new backup codes (invalidates old ones)"""
        if not user.mfa_enabled:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='MFA not enabled for user')

        # Verify current TOTP code
        if not self.verify_mfa_code(user, verification_code):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid verification code')

        # Generate new backup codes
        new_backup_codes = self.totp_service.generate_backup_codes()
        hashed_codes = [self.totp_service.hash_backup_code(code) for code in new_backup_codes]
        user.mfa_backup_codes = hashed_codes

        self.db.commit()
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
