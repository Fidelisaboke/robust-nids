from fastapi import APIRouter, Depends, status

from backend.api.dependencies import get_current_active_user, require_permissions
from backend.database.models import User
from backend.schemas.users import UserCreate, UserOut, UserUpdate
from backend.services.user_service import UserService
from backend.utils.enums import SystemPermissions

router = APIRouter(prefix='/api/v1/users', tags=['Users'])

MANAGE_USERS_PERMISSION = SystemPermissions.MANAGE_USERS


@router.post(
    '/',
    response_model=UserOut,
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user_data: UserCreate, user_service: UserService = Depends()):
    """
    Create a user.

    Args:
        user_data: Details of the user to create.
        user_service (UserService): The user service dependency.

    Returns:
        User: The created user object.
    """
    return user_service.create_user(user_data)


@router.get(
    '/',
    response_model=list[UserOut],
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
    status_code=status.HTTP_200_OK,
)
async def list_users(user_service: UserService = Depends()):
    """
    List all users in the system.

    Returns:
        list[UserOut]: A list of user objects.
        user_service (UserService): The user service dependency.
    """
    return user_service.list_users()


@router.get(
    '/{user_id}',
    response_model=UserOut,
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
    status_code=status.HTTP_200_OK,
)
async def get_user(user_id: int, user_service: UserService = Depends()):
    """
    Get a user by their ID.

    Args:
        user_id (int): The ID of the user to retrieve.
        user_service (UserService): The user service dependency.

    Returns:
        User: The user object.
    """
    return user_service.get_user(user_id)


@router.put(
    '/{user_id}',
    response_model=UserOut,
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
    status_code=status.HTTP_200_OK,
)
async def update_user(user_id: int, user_data: UserUpdate, user_service: UserService = Depends()):
    """
    Update a user's information.

    Args:
        user_id (int): The ID of the user to update.
        user_data (UserUpdate): Fields to update for user.
        user_service (UserService): The user service dependency.

    Returns:
        User: The updated user object.
    """
    return user_service.update_user(user_id, user_data)


@router.delete(
    '/{user_id}',
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_id: int, user_service: UserService = Depends()):
    """
    Delete a user.

    Args:
        user_id (int): The ID of the user.
        user_service (UserService): The user service dependency.

    Returns:
        dict: A message indicating the delete status.
    """
    return user_service.delete_user(user_id)


@router.post(
    '/{user_id}/reset-mfa',
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
)
def admin_reset_user_mfa(
    user_id: int,
    admin_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(),
):
    """
    Admin endpoint to reset a user's MFA settings.

    Args:
        user_id (int): The ID of the user whose MFA settings are to be reset.
        admin_user (User): The admin user performing the action.
        user_service (UserService): The user service dependency.

    """
    user_service.admin_reset_mfa_for_user(user_id, admin_user)
    return {'detail': 'MFA has been reset for the user.'}
