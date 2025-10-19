from fastapi import Depends
from pydantic import EmailStr

from core.dependencies import get_user_repository
from core.security import get_password_hash, verify_password
from database.models import User
from database.repositories.user import UserRepository
from services.token_service import URLTokenService, get_url_token_service


class AuthService:
    def __init__(self, user_repo: UserRepository, token_service: URLTokenService) -> None:
        self.user_repo = user_repo
        self.token_service = token_service

    def authenticate(self, email: EmailStr, password: str) -> User | None:
        """Authenticate user by email and password."""
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def update_password(self, user: User, new_password: str) -> None:
        """Update user's password."""
        user.password_hash = get_password_hash(new_password)
        self.user_repo.session.commit()

    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user's password and clear reset token."""
        if not self.token_service.verify_password_reset_token(token):
            return False

        user = self.token_service.get_user_from_password_token(token)
        if not user:
            return False

        user.password_hash = get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_token_expires = None
        self.user_repo.session.commit()
        return True

# Dependency injection method
def get_auth_service(
        user_repo: UserRepository = Depends(get_user_repository),
        token_service: URLTokenService = Depends(get_url_token_service)
) -> AuthService:
    """Returns an instance of AuthService with dependencies injected."""
    return AuthService(user_repo, token_service)
