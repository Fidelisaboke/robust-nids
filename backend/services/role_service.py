from typing import List

from fastapi import Depends

from core.dependencies import get_permission_repository, get_role_repository
from database.models import Role
from database.repositories.permission import PermissionRepository
from database.repositories.role import RoleRepository
from schemas.roles import RoleCreate, RoleUpdate


class RoleService:
    """Service for managing role operations."""

    def __init__(self, role_repo: RoleRepository, permission_repo: PermissionRepository):
        self.role_repo = role_repo
        self.permission_repo = permission_repo

    def create_role(self, role_data: RoleCreate) -> Role:
        role_dict = role_data.model_dump()
        new_role = self.role_repo.create(role_dict)
        self.role_repo.session.flush()
        self.role_repo.session.refresh(new_role)
        return new_role

    def get_role(self, role_id: int) -> Role:
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise Exception("Role not found")
        return role

    def list_roles(self) -> List[Role]:
        return self.role_repo.list_all()

    def update_role(self, role_id: int, update_data: RoleUpdate) -> Role:
        role = self.get_role(role_id)
        update_dict = update_data.model_dump(exclude_unset=True)
        updated_role = self.role_repo.update(role, update_dict)
        self.role_repo.session.flush()
        self.role_repo.session.refresh(updated_role)
        return updated_role

    def delete_role(self, role_id: int) -> None:
        role = self.get_role(role_id)
        self.role_repo.delete(role)


# Dependency injection
def get_role_service(
    role_repo: RoleRepository = Depends(get_role_repository),
    permission_repo: PermissionRepository = Depends(get_permission_repository),
) -> RoleService:
    return RoleService(role_repo, permission_repo)
