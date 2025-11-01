from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from api.dependencies import require_permissions
from schemas.roles import RoleCreate, RoleOut, RoleUpdate
from services.role_service import RoleService, get_role_service
from utils.enums import SystemPermissions

# Roles router
router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])

MANAGE_ROLES_PERMISSION = SystemPermissions.MANAGE_ROLES


@router.post(
    "/",
    response_model=RoleOut,
    dependencies=[Depends(require_permissions(MANAGE_ROLES_PERMISSION))],
    status_code=status.HTTP_201_CREATED,
)
async def create_role(role_data: RoleCreate, role_service: RoleService = Depends(get_role_service)):
    """
    Create a role.

    Args:
        role_data: Details of the role to create.
        role_service (RoleService): The role service dependency.

    Returns:
        Role: The created role object.
    """
    return role_service.create_role(role_data)


@router.get(
    "/",
    response_model=Page[RoleOut],
    dependencies=[Depends(require_permissions(MANAGE_ROLES_PERMISSION))],
    status_code=status.HTTP_200_OK,
)
async def list_roles(role_service: RoleService = Depends(get_role_service)) -> Page[RoleOut]:
    """
    List all roles in the system.

    Returns:
        Page[RoleOut]: A paginated list of role objects.
        role_service (RoleService): The role service dependency.
    """
    return paginate(role_service.role_repo.session, role_service.list_roles())


@router.get(
    "/{role_id}",
    response_model=RoleOut,
    dependencies=[Depends(require_permissions(MANAGE_ROLES_PERMISSION))],
    status_code=status.HTTP_200_OK,
)
async def get_role(role_id: int, role_service: RoleService = Depends(get_role_service)):
    """
    Get a role by its ID.

    Args:
        role_id (int): The ID of the role to retrieve.
        role_service (RoleService): The role service dependency.

    Returns:
        Role: The role object.
    """
    return role_service.get_role(role_id)


@router.put(
    "/{role_id}",
    response_model=RoleOut,
    dependencies=[Depends(require_permissions(MANAGE_ROLES_PERMISSION))],
    status_code=status.HTTP_200_OK,
)
async def update_role(
    role_id: int, role_data: RoleUpdate, role_service: RoleService = Depends(get_role_service)
):
    """
    Update a role's information.

    Args:
        role_id (int): The ID of the role to update.
        role_data (RoleUpdate): Fields to update for role.
        role_service (RoleService): The role service dependency.

    Returns:
        Role: The updated role object.
    """
    return role_service.update_role(role_id, role_data)


@router.delete(
    "/{role_id}",
    dependencies=[Depends(require_permissions(MANAGE_ROLES_PERMISSION))],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_role(role_id: int, role_service: RoleService = Depends(get_role_service)):
    """
    Delete a role.

    Args:
        role_id (int): The ID of the role.
        role_service (RoleService): The role service dependency.

    Returns:
        dict: A message indicating the delete status.
    """
    return role_service.delete_role(role_id)
