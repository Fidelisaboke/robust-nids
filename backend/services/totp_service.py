import base64
import hashlib
import io
import secrets
from typing import List

import bcrypt
import pyotp
import qrcode

from core.config import settings


class TOTPService:
    def __init__(self):
        self.issuer_name = settings.APP_NAME

    @staticmethod
    def generate_totp_secret() -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()

    def generate_totp_uri(self, secret: str, email: str) -> str:
        """Generate TOTP URI for QR code"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=self.issuer_name)

    @staticmethod
    def generate_qr_code(totp_uri: str) -> str:
        """Generate QR code as base64 string"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color='black', back_color='white')
        img_bytes = io.BytesIO()
        img.save(img_bytes)
        img_bytes.seek(0)
        return base64.b64encode(img_bytes.getvalue()).decode()

    @staticmethod
    def verify_totp_code(secret: str, code: str) -> bool:
        """Verify TOTP code with drift tolerance"""
        if not secret or not code:
            return False
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)  # Allow 30-second drift

    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """Generate cryptographically secure backup codes"""
        backup_codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric codes
            code = secrets.token_urlsafe(8).upper().replace('_', '').replace('-', '')[:8]
            # Format as XXXX-XXXX for readability
            formatted_code = f'{code[:4]}-{code[4:]}'
            backup_codes.append(formatted_code)
        return backup_codes

    @staticmethod
    def hash_backup_code(code: str) -> str:
        """Hash a verification code."""
        return bcrypt.hashpw(code.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

    @staticmethod
    def verify_backup_code(provided_code: str, stored_codes: list[str]) -> tuple[bool, list[str]]:
        """Verify a backup code and return updated list if valid."""
        for hashed in stored_codes:
            if bcrypt.checkpw(provided_code.encode(), hashed.encode()):
                updated = [c for c in stored_codes if c != hashed]
                return True, updated
        return False, stored_codes

    @staticmethod
    def hash_searchable_token(token: str) -> str:
        """Hash a token for secure storage and searching."""
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

# Singleton instance
totp_service = TOTPService()
