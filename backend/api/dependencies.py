"""
Dependencies for user-dependent routes and operations.
"""

from fastapi import Depends, HTTPException, status

from backend.services.auth_service import get_current_active_user


def require_permissions(*permissions: str):
    """Ensure the current user has all specified permissions."""

    def dependency(user=Depends(get_current_active_user)):
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Not authenticated',
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Inactive user',
            )

        # Flatten all user permissions into a set for easy checking
        user_permissions = {perm.name for role in user.roles for perm in role.permissions}
        missing_permissions = [perm for perm in permissions if perm not in user_permissions]

        # Deny access if any required permission is missing
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='You are not authorized to perform this action'
            )

        return True

    return dependency
