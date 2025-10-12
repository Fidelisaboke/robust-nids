from typing import Type

from backend.database.models import Permission
from backend.database.repositories.base import BaseRepository
from backend.schemas.permissions import PermissionCreate, PermissionUpdate


class PermissionRepository(BaseRepository):
    def get_by_id(self, permission_id: int) -> Permission | None:
        """Fetch a permission by ID."""
        return self.session.query(Permission).filter(Permission.id == permission_id).first()

    def get_by_name(self, name: str) -> Permission | None:
        """Fetch permission by name."""
        return self.session.query(Permission).filter(Permission.name == name).first()

    def list_all(self) -> list[Type[Permission]]:
        """Return all permissions."""
        return self.session.query(Permission).all()

    def create(self, data: PermissionCreate) -> Permission:
        """Create a new permission and persist."""
        new_permission = Permission(**data.model_dump())
        self.session.add(new_permission)
        return new_permission

    def update(self, permission: Permission, data: PermissionUpdate) -> Permission:
        """Update an existing permission."""
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(permission, key, value)
        return permission

    def delete(self, permission: Permission) -> None:
        """Delete a permission by ID."""
        self.session.delete(permission)
