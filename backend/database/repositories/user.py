from datetime import datetime, timezone
from typing import Type

from pydantic import EmailStr
from sqlalchemy.orm import joinedload

from backend.database.models import Role, User
from backend.database.repositories.base import BaseRepository
from backend.schemas.users import UserCreate, UserUpdate


class UserRepository(BaseRepository):
    """Repository for user-specific database access."""

    def get_by_id(self, user_id: int) -> User | None:
        """Fetch user by ID with roles and permissions."""
        return (
            self.session.query(User)
            .options(joinedload(User.roles).joinedload(Role.permissions))
            .filter(User.id == user_id)
            .first()
        )

    def get_by_email(self, email: EmailStr) -> User | None:
        """Fetch user by email with roles and permissions."""
        return (
            self.session.query(User)
            .options(joinedload(User.roles).joinedload(Role.permissions))
            .filter(User.email == email)
            .first()
        )

    def get_by_username(self, username: str) -> User | None:
        """Fetch user by username with roles and permissions."""
        return (
            self.session.query(User)
            .options(joinedload(User.roles).joinedload(Role.permissions))
            .filter(User.username == username)
            .first()
        )

    def get_by_mfa_recovery_token(self, token: str) -> User | None:
        """Fetch user by MFA recovery token."""
        return (
            self.session.query(User)
            .filter(
                User.mfa_recovery_token == token,
                User.mfa_recovery_token_expires.isnot(None),
                User.mfa_recovery_token_expires > datetime.now(timezone.utc),
            )
            .first()
        )

    def list_all(self, active_only: bool = False) -> list[Type[User]]:
        """Return all users, optionally filtering by active status."""
        query = self.session.query(User).options(joinedload(User.roles))
        if active_only:
            query = query.filter(User.is_active.is_(True))
        return query.all()

    def create(self, data: UserCreate) -> User:
        """Create a new user."""
        new_user = User(**data.model_dump())
        self.session.add(new_user)
        return new_user

    def update(self, user: User, data: UserUpdate) -> User:
        """Update an existing user."""
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        return user

    def delete(self, user: User) -> None:
        """Delete user."""
        self.session.delete(user)
