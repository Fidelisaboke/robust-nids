from pydantic import BaseModel, ConfigDict

from schemas.permissions import PermissionOut


class RoleOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    permissions: list[PermissionOut] = []

    model_config = ConfigDict(from_attributes=True)


class RoleCreate(BaseModel):
    name: str
    description: str | None = None


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
