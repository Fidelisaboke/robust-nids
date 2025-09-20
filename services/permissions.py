from database.db import db
from database.models import Permission, Role
from utils.permissions import SystemPermissions


class PermissionService:
    def __init__(self):
        self._ensure_system_permissions_exist()

    @staticmethod
    def _ensure_system_permissions_exist():
        """Ensure all system permissions are created in database"""
        with db.get_session() as session:
            for perm_enum in SystemPermissions:
                permission = session.query(Permission).filter(Permission.name == perm_enum.value).first()
                if not permission:
                    new_perm = Permission(
                        name=perm_enum.value,
                        description=f"System permission: {perm_enum.value}"
                    )
                    session.add(new_perm)
            session.commit()

    @staticmethod
    def get_permission_by_name(permission_name):
        with db.get_session() as session:
            return session.query(Permission).filter(Permission.name == permission_name).first()

    @staticmethod
    def assign_permission_to_role(role_name, permission_name):
        """Assign a permission to a role"""
        with db.get_session() as session:
            role = session.query(Role).filter(Role.name == role_name).first()
            permission = session.query(Permission).filter(Permission.name == permission_name).first()

            if role and permission and permission not in role.permissions:
                role.permissions.append(permission)
                return True
            return False

    @staticmethod
    def user_has_permission(user_id, permission_name):
        """Check if a user has a specific permission through their roles"""
        with db.get_session() as session:
            from database.models import User
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            # Check if any of the user's roles have the requested permission
            for role in user.roles:
                for permission in role.permissions:
                    if permission.name == permission_name:
                        return True
            return False

    @staticmethod
    def get_user_permissions(user_id):
        """Get all permissions for a user"""
        with db.get_session() as session:
            from database.models import User
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return set()

            permissions = set()
            for role in user.roles:
                for permission in role.permissions:
                    permissions.add(permission.name)
            return permissions


# Initialise the permission service
permission_service = PermissionService()
