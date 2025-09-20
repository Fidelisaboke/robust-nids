from database.db import db
from database.models import Role, User
from utils.roles import SystemRoles


class RoleService:
    def __init__(self):
        self._ensure_system_roles_exist()

    @staticmethod
    def _ensure_system_roles_exist():
        """Ensure all system roles are created in database."""
        with db.get_session() as session:
            for role_enum in SystemRoles:
                role = session.query(Role).filter(Role.name == role_enum.value).first()
                if not role:
                    new_role = Role(name=role_enum.value)
                    session.add(new_role)
            session.commit()

    @staticmethod
    def get_role_by_name(role_name: str) -> Role:
        with db.get_session() as session:
            return session.query(Role).filter(Role.name == role_name).first()

    @staticmethod
    def get_all_roles():
        with db.get_session() as session:
            return session.query(Role).order_by(Role.name).all()

    @staticmethod
    def user_has_role(user_id: int, role_name: str) -> bool:
        with db.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            return any(role.name == role_name for role in user.roles)

    @staticmethod
    def assign_role_to_user(user_id: int, role_name: str):
        with db.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            role = session.query(Role).filter(Role.name == role_name).first()

            if user and role and role not in user.roles:
                user.roles.append(role)
                return True
            return False


# Initialise role service to ensure system roles exist
role_service = RoleService()
