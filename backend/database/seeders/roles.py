from backend.database.models import Role
from backend.utils.enums import SystemRoles
from .base import BaseSeeder


class RoleSeeder(BaseSeeder):
    """Seeder for system roles"""

    @classmethod
    def run(cls):
        from backend.database.db import db

        with db.get_session() as session:
            # Get existing roles to avoid duplicates
            existing_roles = {r.name for r in session.query(Role).all()}

            roles_to_create = []
            for role_enum in SystemRoles:
                if role_enum.value not in existing_roles:
                    roles_to_create.append(Role(name=role_enum.value))

            if roles_to_create:
                session.add_all(roles_to_create)
                session.commit()
                cls.log_seeding('Role', len(roles_to_create))
            else:
                print('⏩ Roles already seeded, skipping...')
