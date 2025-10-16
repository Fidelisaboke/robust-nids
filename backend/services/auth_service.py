from fastapi import Depends
from pydantic import EmailStr

from core.dependencies import get_user_repository
from core.security import verify_password
from database.models import User
from database.repositories.user import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository = Depends(get_user_repository)):
        self.user_repo = user_repo

    def authenticate(self, email: EmailStr, password: str) -> User | None:
        """Authenticate user by email and password."""
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user
