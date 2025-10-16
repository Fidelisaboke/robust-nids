import bcrypt
import pytest
from fastapi.testclient import TestClient

from api.main import app
from database.db import db
from database.models import User
from database.repositories.permission import PermissionRepository
from database.repositories.role import RoleRepository
from utils.enums import SystemPermissions, SystemRoles

client = TestClient(app)


@pytest.fixture(scope='function')
def non_mfa_user():
    password = 'nomfa'
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with db.get_session() as session:
        user = User(
            email='nomfa@example.com',
            password_hash=hashed,
            is_active=True,
            username='nomfauser',
            mfa_enabled=False,
            mfa_secret=None,
            mfa_method='totp',
            mfa_backup_codes=None,
        )
        session.add(user)
        session.commit()
        yield user
        session.delete(user)
        session.commit()


@pytest.fixture(scope='function')
def mfa_user():
    password = 'mfapass'
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    # Use formatted backup codes and hash them as backend expects
    backup_codes = ['CODE1-CODE2', 'CODE3-CODE4']
    hashed_backup_codes = [bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode() for code in backup_codes]
    with db.get_session() as session:
        user = User(
            email='mfa@example.com',
            password_hash=hashed,
            is_active=True,
            username='mfauser',
            mfa_enabled=True,
            mfa_secret='JBSWY3DPEHPK3PXP',  # Known TOTP secret for tests
            mfa_method='totp',
            mfa_backup_codes=hashed_backup_codes,
        )
        session.add(user)
        session.commit()
        yield user
        session.delete(user)
        session.commit()


@pytest.fixture(scope='function')
def admin_user():
    password = 'adminpass'
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with db.get_session() as session:
        role_repo = RoleRepository(session)
        perm_repo = PermissionRepository(session)

        # Ensure manage_users permission exists
        manage_users_perm = perm_repo.get_by_name(SystemPermissions.MANAGE_USERS)
        if not manage_users_perm:
            permission_data = {'name': SystemPermissions.MANAGE_USERS}
            manage_users_perm = perm_repo.create(permission_data)

        # Ensure admin role exists and has permission
        admin_role = role_repo.get_by_name(SystemRoles.ADMIN)
        if not admin_role:
            role_data = {'name': SystemRoles.ADMIN}
            admin_role = role_repo.create(role_data)
        if manage_users_perm not in admin_role.permissions:
            role_repo.add_permission(admin_role, manage_users_perm)
            session.commit()

        user = User(
            email='mock_admin_test@example.com',
            password_hash=hashed,
            is_active=True,
            username='mockadminuser',
            roles=[admin_role],
        )
        session.add(user)
        session.commit()
        yield user
        session.delete(user)
        session.commit()
