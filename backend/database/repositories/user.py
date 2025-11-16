from datetime import datetime, timezone
from hmac import compare_digest

from pydantic import EmailStr
from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from database.models import Role, User
from database.repositories.base import BaseRepository


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

    def get_existing_user(self, email: EmailStr, username: str) -> User | None:
        """Check for existing user by email or username (for uniqueness checks)."""
        return self.session.query(User).filter((User.email == email) | (User.username == username)).first()

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

    def get_by_email_verification_token(self, token: str) -> User | None:
        """Fetch user by email verification token."""
        users = (
            self.session.query(User)
            .filter(
                User.email_verification_token_expires.isnot(None),
                User.email_verification_token_expires > datetime.now(timezone.utc),
            )
            .all()
        )

        # Use constant-time comparison
        for user in users:
            if user.email_verification_token and compare_digest(user.email_verification_token, token):
                return user

        return None

    def get_by_password_reset_token(self, token: str) -> User | None:
        """Fetch user by password reset token."""
        return (
            self.session.query(User)
            .filter(
                User.password_reset_token == token,
                User.password_reset_token_expires.isnot(None),
                User.password_reset_token_expires > datetime.now(timezone.utc),
            )
            .first()
        )

    def list_all(
        self,
        is_active: bool | None = None,
        created_after: datetime | None = None,
        role: str | None = None,
        email_verified: bool | None = None,
        account_status: str | None = None,
        search: str | None = None,
    ):
        """Return a SQLAlchemy Select for all users, with optional filters.
        Args:
            is_active (bool | None): If provided, only return users with the specified active status.
            created_after (datetime | None): If provided, only return users created after this date.
            role (str | None): If provided, only return users with the specified role.
            email_verified (bool | None): If provided, filter by email verification status.
            account_status (str | None): If provided, filter by account status.
            search (str | None): If provided, filter users by search term.
        Returns:
            Select: SQLAlchemy Select statement for users.
        """
        stmt = select(User).options(joinedload(User.roles))
        if is_active is not None:
            stmt = stmt.where(User.is_active.is_(is_active))
        if created_after:
            stmt = stmt.where(User.created_at > created_after)
        if role:
            stmt = stmt.join(User.roles).where(Role.name == role)
        if email_verified is not None:
            stmt = stmt.where(User.email_verified.is_(email_verified))
        if account_status is not None:
            stmt = stmt.where(User.account_status == account_status)
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    User.username.ilike(search_term),
                    User.email.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term)
                )
            )
        return stmt

    def create(self, data: dict) -> User:
        """Create a new user."""
        new_user = User(**data)
        self.session.add(new_user)
        return new_user

    def update(self, user: User, data: dict) -> User:
        """Update an existing user."""
        for key, value in data.items():
            setattr(user, key, value)
        return user

    def delete(self, user: User) -> None:
        """Delete user."""
        self.session.delete(user)
