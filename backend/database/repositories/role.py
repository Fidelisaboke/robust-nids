from typing import Type

from sqlalchemy.orm import joinedload

from backend.database.models import Permission, Role
from backend.database.repositories.base import BaseRepository


class RoleRepository(BaseRepository):
    """Repository for role-specific data access."""

    def get_by_id(self, role_id: int) -> Role | None:
        """Fetch role by ID with permissions."""
        return (
            self.session.query(Role).options(joinedload(Role.permissions)).filter(Role.id == role_id).first()
        )

    def get_by_name(self, name: str) -> Role | None:
        """Fetch role by name with permissions."""
        return (
            self.session.query(Role).options(joinedload(Role.permissions)).filter(Role.name == name).first()
        )

    def list_all(self) -> list[Type[Role]]:
        """Return all roles."""
        return self.session.query(Role).options(joinedload(Role.permissions)).all()

    def create(self, data: dict) -> Role:
        """Create a new role."""
        new_role = Role(**data)
        self.session.add(new_role)
        return new_role

    def update(self, role: Role, data: dict) -> Role:
        """Update an existing role."""
        for key, value in data.items():
            setattr(role, key, value)
        return role

    def delete(self, role: Role) -> None:
        """Delete a role."""
        self.session.delete(role)

    def add_permission(self, role: Role, permission: Permission) -> None:
        """Assign a permission to a role."""
        if permission not in role.permissions:
            role.permissions.append(permission)

    def remove_permission(self, role: Role, permission: Permission) -> None:
        if permission in role.permissions:
            role.permissions.remove(permission)
