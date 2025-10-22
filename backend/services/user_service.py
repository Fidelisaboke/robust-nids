from datetime import datetime, timezone
from typing import Type

from fastapi import Depends

from core.config import settings
from core.dependencies import get_role_repository, get_user_repository
from core.security import get_password_hash
from database.models import User
from database.repositories.role import RoleRepository
from database.repositories.user import UserRepository
from schemas.users import UserCreate, UserUpdate
from services.exceptions.user import (
    EmailAlreadyExistsError,
    RoleNotAssignedError,
    RoleNotFoundError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)
from services.mfa_service import MFAService, get_mfa_service


class UserService:
    """Service for managing user operations."""

    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        mfa_service: MFAService,
    ):
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.mfa_service = mfa_service

    def create_user(self, user_data: UserCreate) -> User:
        """Handles the creation of a new user."""
        if self.user_repo.get_by_email(user_data.email):
            raise EmailAlreadyExistsError()

        if self.user_repo.get_by_username(user_data.username):
            raise UsernameAlreadyExistsError()

        # Hash password
        password_hash = get_password_hash(user_data.password)
        user_dict = user_data.model_dump()
        user_dict["password_hash"] = password_hash
        user_dict.pop("password", None)

        # Default preferences
        user_dict["preferences"] = settings.DEFAULT_USER_PREFERENCES

        # Assign roles
        if not user_dict.get("roles"):
            raise RoleNotAssignedError()
        user_dict["roles"] = self._handle_role_updates(user_dict)

        new_user = self.user_repo.create(user_dict)
        self.user_repo.session.flush()
        self.user_repo.session.refresh(new_user)
        return new_user

    def get_user(self, user_id: int) -> User:
        """Fetch a user by ID."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    def list_users(self, active_only: bool = False) -> list[Type[User]]:
        """List all users, optionally filtering by active status."""
        return self.user_repo.list_all(active_only=active_only)

    def update_user(self, user_id: int, update_data: UserUpdate) -> User:
        """Handles updating an existing user."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        update_dict = update_data.model_dump(exclude_unset=True)

        # Validate uniqueness
        if "email" in update_dict and update_dict["email"] != user.email:
            if self.user_repo.get_by_email(update_dict["email"]):
                raise EmailAlreadyExistsError()

        if "username" in update_dict and update_dict["username"] != user.username:
            if self.user_repo.get_by_username(update_dict["username"]):
                raise UsernameAlreadyExistsError()

        if "password" in update_dict:
            update_dict["password_hash"] = get_password_hash(update_dict.pop("password"))

        # Handle role updates
        if "roles" in update_dict:
            update_dict["roles"] = self._handle_role_updates(update_dict)

        # Merge preferences
        if "preferences" in update_dict:
            current_prefs = user.preferences or {}
            update_dict["preferences"] = {**current_prefs, **update_dict["preferences"]}

        update_dict["last_profile_update"] = datetime.now(timezone.utc)

        updated_user = self.user_repo.update(user, update_dict)
        self.user_repo.session.flush()
        self.user_repo.session.refresh(updated_user)
        return updated_user

    def delete_user(self, user_id: int) -> None:
        """Handles deleting a user."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        self.user_repo.delete(user)

    def activate_user(self, user_id: int) -> User | None:
        """Activate a user account."""
        user = self.get_user(user_id)
        if not user:
            raise UserNotFoundError()

        if user.is_active:
            raise ValueError("User account is already active.")

        updated_user = self.user_repo.update(user, {"is_active": True})
        self.user_repo.session.flush()
        self.user_repo.session.refresh(updated_user)
        return updated_user

    def deactivate_user(self, user_id: int) -> User | None:
        """Deactivate a user account."""
        user = self.get_user(user_id)
        if not user:
            raise UserNotFoundError()

        if not user.is_active:
            raise ValueError("User account is already deactivated.")

        updated_user = self.user_repo.update(user, {"is_active": False})
        self.user_repo.session.flush()
        self.user_repo.session.refresh(updated_user)
        return updated_user

    def admin_reset_mfa_for_user(self, user_id: int, admin_user: User):
        user_to_reset = self.get_user(user_id)
        self.mfa_service.admin_disable_mfa(user_to_reset, admin_user)

    def _handle_role_updates(self, data: dict):
        """Replace role IDs with actual Role objects."""
        role_objects = []
        for role_id in data["roles"]:
            role = self.role_repo.get_by_id(role_id)
            if not role:
                raise RoleNotFoundError(role_id)
            role_objects.append(role)
        return role_objects


# Dependency injection
def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    role_repo: RoleRepository = Depends(get_role_repository),
    mfa_service: MFAService = Depends(get_mfa_service),
) -> UserService:
    """Returns an instance of UserService with dependencies injected."""
    return UserService(user_repo, role_repo, mfa_service)
