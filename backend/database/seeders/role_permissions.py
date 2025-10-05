from backend.database.models import Permission, Role
from backend.utils.enums import SystemPermissions, SystemRoles

from .base import BaseSeeder


class RolePermissionSeeder(BaseSeeder):
    """Programmatic role-permission mapping using enum"""

    # Base permissions that everyone gets
    BASE_PERMISSIONS = {
        SystemPermissions.VIEW_DASHBOARD,
        SystemPermissions.VIEW_LIVE_MONITOR,
        SystemPermissions.VIEW_ALERTS,
    }

    # Additional permissions for each role
    ROLE_EXTRA_PERMISSIONS = {
        SystemRoles.ANALYST: {
            SystemPermissions.UPDATE_ALERT_STATUS,
            SystemPermissions.VIEW_ANALYTICS,
            SystemPermissions.EXPORT_DATA,
            SystemPermissions.VIEW_DATA_EXPLORER,
            SystemPermissions.ACCESS_RAW_DATA,
            SystemPermissions.VIEW_MODELS,
        },
        SystemRoles.MANAGER: {
            SystemPermissions.TRAIN_MODELS,
            SystemPermissions.VIEW_SETTINGS,
            SystemPermissions.VIEW_LOGS,
        },
        SystemRoles.ADMIN: set(SystemPermissions),
    }

    @classmethod
    def run(cls):
        from backend.database.db import db

        with db.get_session() as session:
            # Load all roles and permissions
            roles = session.query(Role).all()
            permissions = session.query(Permission).all()

            role_dict = {role.name: role for role in roles}
            perm_dict = {perm.name: perm for perm in permissions}

            assignments_made = 0

            # Build permission sets for each role
            role_permission_sets = {}
            for role_name in role_dict.keys():
                if role_name == 'viewer':
                    role_permission_sets[role_name] = cls.BASE_PERMISSIONS
                else:
                    role_permission_sets[role_name] = cls.BASE_PERMISSIONS | cls.ROLE_EXTRA_PERMISSIONS.get(
                        role_name, set()
                    )

            # Assign permissions to roles
            for role_name, permission_enums in role_permission_sets.items():
                role = role_dict.get(role_name)
                if not role:
                    continue

                for permission_enum in permission_enums:
                    permission_name = permission_enum.value
                    permission = perm_dict.get(permission_name)
                    if permission and permission not in role.permissions:
                        role.permissions.append(permission)
                        assignments_made += 1

            if assignments_made > 0:
                session.commit()
                cls.log_seeding('Role-Permission', assignments_made)
            else:
                print('⏩ Role permissions already assigned, skipping...')
