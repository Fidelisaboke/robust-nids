from database.models import Permission
from utils.permissions import SystemPermissions
from .base import BaseSeeder


class PermissionSeeder(BaseSeeder):
    """Seeder for system permissions"""

    @classmethod
    def run(cls):
        from database.db import db

        with db.get_session() as session:
            # Get existing permissions to avoid duplicates
            existing_permissions = {p.name for p in session.query(Permission).all()}

            permissions_to_create = []
            for perm_enum in SystemPermissions:
                if perm_enum.value not in existing_permissions:
                    permissions_to_create.append(
                        Permission(
                            name=perm_enum.value,
                            description=f"System permission: {perm_enum.name}",
                        )
                    )

            if permissions_to_create:
                session.add_all(permissions_to_create)
                session.commit()
                cls.log_seeding("Permission", len(permissions_to_create))
            else:
                print("⏩ Permissions already seeded, skipping...")
