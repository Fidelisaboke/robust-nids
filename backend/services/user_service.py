from datetime import datetime, timezone
from typing import Type

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.api.schemas.users import UserCreate, UserUpdate
from backend.core.config import settings
from backend.database.models import User
from backend.database.repositories.role import RoleRepository
from backend.database.repositories.user import UserRepository
from backend.services.auth_service import get_password_hash


class UserService:
    """Service for managing user operations."""

    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.role_repo = RoleRepository(session)

    def create_user(self, user_data: UserCreate) -> User:
        """Handles the creation of a new user."""
        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(status_code=400, detail='Email already registered')

        if self.user_repo.get_by_username(user_data.username):
            raise HTTPException(status_code=400, detail='Username already taken')

        # Hash password
        password_hash = get_password_hash(user_data.password)
        user_dict = user_data.model_dump()
        user_dict['password_hash'] = password_hash
        user_dict.pop('password', None)

        # Default preferences
        user_dict['preferences'] = settings.DEFAULT_USER_PREFERENCES

        # Assign roles
        if not user_dict.get('roles'):
            raise HTTPException(status_code=400, detail='At least one role must be assigned to the user')
        user_dict['roles'] = self._handle_role_updates(user_dict)

        new_user = self.user_repo.create(user_dict)
        self.session.commit()
        self.session.refresh(new_user)
        return self.user_repo.get_by_id(new_user.id)

    def get_user(self, user_id: id) -> User:
        """Fetch a user by ID."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail='User not found')
        return user

    def list_users(self, active_only: bool = False) -> list[Type[User]]:
        """List all users, optionally filtering by active status."""
        return self.user_repo.list_all(active_only=active_only)

    def update_user(self, user_id: int, update_data: UserUpdate) -> User:
        """Handles updating an existing user."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail='User not found')

        update_dict = update_data.model_dump(exclude_unset=True)

        # Validate uniqueness
        if 'email' in update_dict and update_dict['email'] != user.email:
            if self.user_repo.get_by_email(update_dict['email']):
                raise HTTPException(status_code=400, detail='Email already registered')

        if 'username' in update_dict and update_dict['username'] != user.username:
            if self.user_repo.get_by_username(update_dict['username']):
                raise HTTPException(status_code=400, detail='Username already taken')

        if 'password' in update_dict:
            update_dict['password_hash'] = get_password_hash(update_dict.pop('password'))

        # Handle role updates
        if 'roles' in update_dict:
            update_dict['roles'] = self._handle_role_updates(update_dict)

        # Merge preferences
        if 'preferences' in update_dict:
            current_prefs = user.preferences or {}
            update_dict['preferences'] = {**current_prefs, **update_dict['preferences']}

        update_dict['last_profile_update'] = datetime.now(timezone.utc)

        updated_user = self.user_repo.update(user, update_dict)
        self.session.commit()
        self.session.refresh(updated_user)
        return self.user_repo.get_by_id(updated_user.id)

    def delete_user(self, user_id: int) -> None:
        """Handles deleting a user."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail='User not found')

        self.user_repo.delete(user)
        self.session.commit()

    def _handle_role_updates(self, data: dict):
        """Replace role IDs with actual Role objects."""
        role_objects = []
        for role_id in data['roles']:
            role = self.role_repo.get_by_id(role_id)
            if not role:
                raise HTTPException(status_code=404, detail=f'Failed to assign role {role_id}: not found')
            role_objects.append(role)
        return role_objects
