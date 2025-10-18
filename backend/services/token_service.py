import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends
from sqlalchemy.orm import Session

from core.config import settings
from core.dependencies import get_db_session, get_user_repository
from database.repositories.user import UserRepository


class URLTokenService:
    def __init__(
        self,
        session: Session,
        user_repo: UserRepository,
    ):
        self.token_length = 32
        self.session = session
        self.user_repo = user_repo

    def generate_token(self) -> str:
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(self.token_length)

    def create_email_verification_token(self, user_id: int) -> str:
        """Create and store email verification token"""
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise ValueError('User not found')

        # Generate token
        token = self.generate_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES
        )

        # Store in database
        user.email_verification_token = token
        user.email_verification_token_expires = expires_at
        self.session.commit()

        return token

    def create_password_reset_token(self, user_id: int) -> str:
        """Create and store password reset token"""
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise ValueError('User not found')

        # Generate token
        token = self.generate_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
        )

        # Store in database
        user.password_reset_token = token
        user.password_reset_token_expires = expires_at
        self.session.commit()

        return token

    def verify_email_verification_token(self, token: str) -> bool:
        """Verify email verification token"""
        user = self.user_repo.get_by_email_verification_token(token)

        if not user:
            return False

        # Check expiration
        if user.email_verification_token_expires < datetime.now(timezone.utc):
            return False

        # Token is valid
        return True

    def verify_password_reset_token(self, token: str) -> bool:
        """Verify password reset token"""
        user = self.user_repo.get_by_password_reset_token(token)

        if not user:
            return False

        # Check expiration
        if user.password_reset_token_expires < datetime.now(timezone.utc):
            return False

        # Token is valid
        return True

    def get_user_from_email_token(self, token: str):
        """Get user from email verification token"""
        return self.user_repo.get_by_email_verification_token(token)

    def get_user_from_password_token(self, token: str):
        """Get user from password reset token"""
        return self.user_repo.get_by_password_reset_token(token)

    def mark_email_as_verified(self, token: str) -> bool:
        """Mark user's email as verified"""
        if not self.verify_email_verification_token(token):
            return False

        user = self.get_user_from_email_token(token)
        if user and not user.email_verified:
            # Mark email as verified
            user.email_verified = True
            user.email_verified_at = datetime.now(timezone.utc)

            # Revoke token
            user.email_verification_token = None
            user.email_verification_token_expires = None

            self.session.commit()
            return True

        return False

    def revoke_email_token(self, user_id: int):
        """Revoke email verification token after use"""
        user = self.user_repo.get_by_id(user_id)

        if user:
            user.email_verification_token = None
            user.email_verification_token_expires = None
            self.session.commit()

    def revoke_password_token(self, user_id: int):
        """Revoke password reset token after use"""
        user = self.user_repo.get_by_id(user_id)

        if user:
            user.password_reset_token = None
            user.password_reset_token_expires = None
            self.session.commit()


# Dependency injector for URLTokenService
def get_url_token_service(
    session: Session = Depends(get_db_session), user_repo: UserRepository = Depends(get_user_repository)
) -> URLTokenService:
    """Returns an instance of URLTokenService with dependencies injected."""
    return URLTokenService(session, user_repo)
