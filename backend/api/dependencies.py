"""
Dependencies for user-dependent routes and operations
"""

from fastapi import Depends, HTTPException, status

from backend.services.auth_service import get_current_user


# Dependency for permission requirements
def require_permissions(*permissions: str):
    def dependency(user=Depends(get_current_user)):
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
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return True

    return dependency
