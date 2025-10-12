from fastapi import APIRouter, Depends, status

from backend.api.dependencies import require_permissions
from backend.api.schemas.users import UserCreate, UserOut, UserUpdate
from backend.database.db import db
from backend.database.models import User
from backend.services.auth_service import get_current_active_user
from backend.services.mfa_service import MFAService
from backend.services.totp_service import totp_service
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
async def create_user(user_data: UserCreate):
    """
    Create a user.

    Args:
        user_data: Details of the user to create.
    Returns:
        User: The created user object.
    """
    with db.get_session() as session:
        user_service = UserService(session)
        return user_service.create_user(user_data)


@router.get(
    '/',
    response_model=list[UserOut],
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
    status_code=status.HTTP_200_OK,
)
async def list_users():
    """
    List all users in the system.

    Returns:
        list[UserOut]: A list of user objects.
    """
    with db.get_session() as session:
        user_service = UserService(session)
        return user_service.list_users()


@router.get(
    '/{user_id}',
    response_model=UserOut,
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
    status_code=status.HTTP_200_OK,
)
async def get_user(user_id: int):
    """
    Get a user by their ID.

    Args:
        user_id (int): The ID of the user to retrieve.

    Returns:
        User: The user object.
    """
    with db.get_session() as session:
        user_service = UserService(session)
        return user_service.get_user(user_id)


@router.put(
    '/{user_id}',
    response_model=UserOut,
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
    status_code=status.HTTP_200_OK,
)
async def update_user(user_id: int, user_data: UserUpdate):
    """
    Update a user's information.

    Args:
        user_id (int): The ID of the user to update.
        user_data (UserUpdate): Fields to update for user.

    Returns:
        User: The updated user object.
    """
    with db.get_session() as session:
        user_service = UserService(session)
        return user_service.update_user(user_id, user_data)


@router.delete(
    '/{user_id}',
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_id: int):
    """
    Delete a user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        dict: A message indicating the delete status.
    """
    with db.get_session() as session:
        user_service = UserService(session)
        user_service.delete_user(user_id)


@router.post(
    "/{user_id}/reset-mfa",
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
    status_code=status.HTTP_204_NO_CONTENT
)
def admin_reset_user_mfa(user_id: int, admin_user: User = Depends(get_current_active_user)):
    """
    Admin endpoint to reset a user's MFA settings.

    Args:
        user_id (int): The ID of the user whose MFA settings are to be reset.
        admin_user (User): The admin user performing the action.

    """
    with db.get_session() as session:
        user_service = UserService(session)
        user_to_reset = user_service.get_user(user_id)

        mfa_service = MFAService(session, totp_service)
        mfa_service.admin_disable_mfa(
            user=session.merge(user_to_reset),
            performing_admin=session.merge(admin_user)
        )
