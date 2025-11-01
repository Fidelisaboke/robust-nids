from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from api.dependencies import get_current_active_user, require_permissions
from database.models import User
from schemas.users import UserCreate, UserOut, UserRoleUpdateRequest, UserRoleUpdateResponse, UserUpdate
from services.email_service import EmailService, get_email_service
from services.exceptions.user import RoleNotFoundError, UserNotFoundError
from services.user_service import UserService, get_user_service
from utils.enums import SystemPermissions

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

MANAGE_USERS_PERMISSION = SystemPermissions.MANAGE_USERS


@router.post(
    "/",
    response_model=UserOut,
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user_data: UserCreate, user_service: UserService = Depends(get_user_service)):
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
    "/",
    response_model=Page[UserOut],
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
    status_code=status.HTTP_200_OK,
)
async def list_users(user_service: UserService = Depends(get_user_service)) -> Page[UserOut]:
    """
    List all users in the system.

    Returns:
        Page[UserOut]: A paginated list of user objects.
        user_service (UserService): The user service dependency.
    """
    return paginate(user_service.user_repo.session, user_service.list_users())


@router.get(
    "/{user_id}",
    response_model=UserOut,
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
    status_code=status.HTTP_200_OK,
)
async def get_user(user_id: int, user_service: UserService = Depends(get_user_service)):
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
    "/{user_id}",
    response_model=UserOut,
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: int, user_data: UserUpdate, user_service: UserService = Depends(get_user_service)
):
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
    "/{user_id}",
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_id: int, user_service: UserService = Depends(get_user_service)):
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
    "/{user_id}/reset-mfa",
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
)
def admin_reset_user_mfa(
    user_id: int,
    admin_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Admin endpoint to reset a user's MFA settings.

    Args:
        user_id (int): The ID of the user whose MFA settings are to be reset.
        admin_user (User): The admin user performing the action.
        user_service (UserService): The user service dependency.

    """
    user_service.admin_reset_mfa_for_user(user_id, admin_user)
    return {"detail": "MFA has been reset for the user."}


@router.post("/{user_id}/activate", dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))])
async def activate_user(
    user_id: int,
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(get_user_service),
    email_service: EmailService = Depends(get_email_service),
):
    """
    Activate a user account.

    Args:
        user_id (int): The ID of the user to activate.
        user_service (UserService): The user service dependency.

    Returns:
        dict: A message indicating the activation status.
    """
    try:
        user = user_service.activate_user(user_id)

        # Send activation notification email to user
        await email_service.send_user_account_activated_email(
            background_tasks=background_tasks,
            user_email=user.email,
            user_name=user.first_name or user.username,
        )

        # Send activation notification email to admins
        await email_service.send_admin_user_account_activated_email(
            background_tasks=background_tasks,
            user_email=user.email,
            user_name=user.first_name or user.username,
        )
        return {"detail": "User account activated successfully."}
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{user_id}/deactivate", dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))])
async def deactivate_user(
    user_id: int,
    background_tasks: BackgroundTasks,
    admin_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
    email_service: EmailService = Depends(get_email_service),
):
    """
    Deactivate a user account.

    Args:
        user_id (int): The ID of the user to deactivate.
        user_service (UserService): The user service dependency.

    Returns:
        dict: A message indicating the deactivation status.
    """
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account.",
        )
    try:
        user = user_service.deactivate_user(user_id)

        # Send deactivation notification email to user
        await email_service.send_user_account_deactivated_email(
            background_tasks=background_tasks,
            user_email=user.email,
            user_name=user.first_name or user.username,
        )

        # Send deactivation notification email to admins
        await email_service.send_admin_user_account_deactivated_email(
            background_tasks=background_tasks,
            user_email=user.email,
            user_name=user.first_name or user.username,
        )
        return {"detail": "User account deactivated successfully."}
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/{user_id}/roles",
    response_model=UserRoleUpdateResponse,
    dependencies=[Depends(require_permissions(MANAGE_USERS_PERMISSION))],
)
async def update_user_roles(
    request: UserRoleUpdateRequest,
    user_id: int,
    admin_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Assign or update a user's roles.

    Args:
        request (UserRoleUpdateRequest): The new list of role IDs to assign to the user.
        user_id (int): The ID of the user whose roles are being updated.
        admin_user (User, optional): The currently authenticated admin user (injected).
        user_service (UserService, optional): The user service dependency (injected).

    Raises:
        HTTPException: 400 if the admin attempts to change their own roles.
        HTTPException: 404 if the user or any role is not found.

    Returns:
        UserRoleUpdateResponse: Details of the update and the updated user object.
    """
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role.",
        )
    try:
        user = user_service.update_user_roles(user_id, request.role_ids)
        return UserRoleUpdateResponse(detail="User role(s) updated successfully.", user=user)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    except RoleNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
