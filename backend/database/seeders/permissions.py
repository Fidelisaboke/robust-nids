from backend.database.models import Permission
from backend.utils.enums import SystemPermissions
from .base import BaseSeeder


class PermissionSeeder(BaseSeeder):
    """Seeder for system permissions"""

    @classmethod
    def run(cls):
        from backend.database.db import db

        with db.get_session() as session:
            existing_permissions = {p.name for p in session.query(Permission).all()}

            permissions_to_create = []
            for perm_enum in SystemPermissions:
                if perm_enum.value not in existing_permissions:
                    # Add category based on permission type
                    category = cls._get_permission_category(perm_enum.name)
                    permissions_to_create.append(
                        Permission(
                            name=perm_enum.value,
                            description=f"System permission: {perm_enum.name}",
                            category=category,
                        )
                    )

            if permissions_to_create:
                session.add_all(permissions_to_create)
                session.commit()
                cls.log_seeding("Permission", len(permissions_to_create))
            else:
                print("⏩ Permissions already seeded, skipping...")

    @classmethod
    def _get_permission_category(cls, permission_name):
        """Categorize permissions for better organization"""
        if permission_name.startswith("VIEW_"):
            return "view"
        elif "ALERT" in permission_name:
            return "alerts"
        elif "MODEL" in permission_name:
            return "models"
        elif "MANAGE" in permission_name or "SYSTEM" in permission_name:
            return "administration"
        else:
            return "general"
