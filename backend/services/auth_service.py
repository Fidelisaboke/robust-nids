from fastapi import Depends
from pydantic import EmailStr

from core.dependencies import get_user_repository
from core.security import get_password_hash, verify_password
from database.models import User
from database.repositories.user import UserRepository
from schemas.auth import (
    UserRegistrationRequest,
    UserRegistrationResponse,
)
from services.exceptions.mfa import InvalidMFAVerificationCodeError, MFAException
from services.exceptions.user import UserAlreadyExistsError
from services.mfa_service import MFAService, get_mfa_service
from services.token_service import URLTokenService, get_url_token_service


class AuthService:
    def __init__(
        self, user_repo: UserRepository, token_service: URLTokenService, mfa_service: MFAService
    ) -> None:
        self.user_repo = user_repo
        self.token_service = token_service
        self.mfa_service = mfa_service

    def authenticate(self, email: EmailStr, password: str) -> User | None:
        """Authenticate user by email and password."""
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def register_user(self, user_data: UserRegistrationRequest) -> UserRegistrationResponse:
        """Register a new user."""
        existing_user = self.user_repo.get_existing_user(user_data.email, user_data.username)
        if existing_user:
            raise UserAlreadyExistsError("A user with this email or username already exists.")

        if user_data.password != user_data.confirm_password:
            raise ValueError("Passwords do not match.")

        hashed_password = get_password_hash(user_data.password)

        # Create new user with inactive status
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            department=user_data.department,
            job_title=user_data.job_title,
            is_active=False,
            email_verified=False,
        )
        self.user_repo.session.add(new_user)
        self.user_repo.session.commit()

        return UserRegistrationResponse(
            id=new_user.id,
            email=new_user.email,
            username=new_user.username,
            detail="Registration successful. Your account is pending admin approval.",
        )

    def update_password(self, user: User, new_password: str) -> None:
        """Update user's password."""
        user.password_hash = get_password_hash(new_password)
        self.user_repo.session.commit()

    def reset_password(self, token: str, new_password: str, mfa_code: str | None = None) -> bool:
        """Reset user's password. Requires MFA verification if enabled."""
        if not self.token_service.verify_password_reset_token(token):
            return False

        user = self.token_service.get_user_from_password_token(token)
        if not user:
            return False

        # Check if MFA is enabled and verify the provided MFA code
        if user.mfa_enabled:
            if not mfa_code:
                raise MFAException("MFA verification required for password reset.")

            if not self.mfa_service.verify_mfa_code(user, mfa_code):
                raise InvalidMFAVerificationCodeError()

        user.password_hash = get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_token_expires = None

        # TODO: Invalidate all active sessions/tokens for the user
        # self.token_service.invalidate_sessions(user)

        self.user_repo.session.commit()
        return True


# Dependency injection method
def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    token_service: URLTokenService = Depends(get_url_token_service),
    mfa_service: MFAService = Depends(get_mfa_service),
) -> AuthService:
    """Returns an instance of AuthService with dependencies injected."""
    return AuthService(user_repo, token_service, mfa_service)
