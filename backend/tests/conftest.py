# Standard library imports
import os

# Third-party imports
import bcrypt
import pytest
from fastapi.testclient import TestClient
from fastapi_mail import ConnectionConfig

# Add FastAPI pagination for tests
from fastapi_pagination import add_pagination

# Local application imports
from api.main import app
from core.config import settings
from database.db import db
from database.models import User
from database.repositories.permission import PermissionRepository
from database.repositories.role import RoleRepository
from services.email_service import EmailService, get_email_service
from utils.enums import SystemPermissions, SystemRoles

add_pagination(app)

test_mail_conf = ConnectionConfig(
    MAIL_USERNAME="test@example.com",
    MAIL_PASSWORD="password",
    MAIL_FROM="test@example.com",
    MAIL_PORT=1025,
    MAIL_SERVER="localhost",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=False,
    MAIL_FROM_NAME="Test",
    SUPPRESS_SEND=1,
    MAIL_DEBUG=1,
    TEMPLATE_FOLDER=settings.TEMPLATE_FOLDER,
)


@pytest.fixture(scope="function")
def test_client():
    app.dependency_overrides[get_email_service] = lambda: EmailService(test_mail_conf)
    return TestClient(app)


@pytest.fixture(scope="function")
def test_user():
    with db.get_session() as session:
        user = User(
            email="verifyme@example.com",
            password_hash="hashedpass",
            is_active=True,
            username="verifyme",
            email_verified=False,
        )
        session.add(user)
        session.commit()
        yield user
        session.delete(user)
        session.commit()


@pytest.fixture(autouse=True, scope="function")
def patch_email_service(monkeypatch):
    monkeypatch.setattr(
        "services.email_service.get_email_service", lambda conf=None: get_email_service(test_mail_conf)
    )


# Global fixture for FastAPI-Mail test directory
@pytest.fixture(scope="session", autouse=True)
def setup_mail_dir():
    MAIL_PATH = "test_emails"
    os.makedirs(MAIL_PATH, exist_ok=True)
    yield
    # Clean up after tests
    for f in os.listdir(MAIL_PATH):
        os.remove(os.path.join(MAIL_PATH, f))


client = TestClient(app)


@pytest.fixture(scope="function")
def non_mfa_user():
    password = "nomfa"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with db.get_session() as session:
        user = User(
            email="nomfa@example.com",
            password_hash=hashed,
            is_active=True,
            username="nomfauser",
            mfa_enabled=False,
            mfa_secret=None,
            mfa_method="totp",
            mfa_backup_codes=None,
            email_verified=True,
        )
        session.add(user)
        session.commit()
        yield user
        session.delete(user)
        session.commit()


@pytest.fixture(scope="function")
def mfa_user():
    password = "mfapass"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    # Use formatted backup codes and hash them as backend expects
    backup_codes = ["CODE1-CODE2", "CODE3-CODE4"]
    hashed_backup_codes = [bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode() for code in backup_codes]
    with db.get_session() as session:
        user = User(
            email="mfa@example.com",
            password_hash=hashed,
            is_active=True,
            username="mfauser",
            mfa_enabled=True,
            mfa_secret="JBSWY3DPEHPK3PXP",  # Known TOTP secret for tests
            mfa_method="totp",
            mfa_backup_codes=hashed_backup_codes,
            email_verified=True,
        )
        session.add(user)
        session.commit()
        yield user
        session.delete(user)
        session.commit()


@pytest.fixture(scope="function")
def admin_user():
    password = "adminpass"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with db.get_session() as session:
        role_repo = RoleRepository(session)
        perm_repo = PermissionRepository(session)

        # Ensure manage_users permission exists
        manage_users_perm = perm_repo.get_by_name(SystemPermissions.MANAGE_USERS)
        if not manage_users_perm:
            permission_data = {"name": SystemPermissions.MANAGE_USERS}
            manage_users_perm = perm_repo.create(permission_data)

        # Ensure admin role exists and has permission
        admin_role = role_repo.get_by_name(SystemRoles.ADMIN)
        if not admin_role:
            role_data = {"name": SystemRoles.ADMIN}
            admin_role = role_repo.create(role_data)
        if manage_users_perm not in admin_role.permissions:
            role_repo.add_permission(admin_role, manage_users_perm)
            session.commit()

        user = User(
            email="mock_admin_test@example.com",
            password_hash=hashed,
            is_active=True,
            username="mockadminuser",
            roles=[admin_role],
            email_verified=True,
        )
        session.add(user)
        session.commit()
        yield user
        session.delete(user)
        session.commit()


# Fixture for an unverified user (for negative tests)
@pytest.fixture(scope="function")
def unverified_user():
    password = "unverified"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with db.get_session() as session:
        user = User(
            email="unverified@example.com",
            password_hash=hashed,
            is_active=True,
            username="unverifieduser",
            mfa_enabled=False,
            mfa_secret=None,
            mfa_method="totp",
            mfa_backup_codes=None,
            email_verified=False,
        )
        session.add(user)
        session.commit()
        yield user
        session.delete(user)
        session.commit()


# Fixture for a test role
@pytest.fixture(scope="function")
def test_role():
    with db.get_session() as session:
        role_repo = RoleRepository(session)
        role_data = {"name": "test_role"}
        role = role_repo.create(role_data)
        session.commit()
        yield role
        # Only delete if still present
        refreshed_role = session.query(type(role)).filter_by(id=role.id).first()
        if refreshed_role is not None:
            session.delete(refreshed_role)
            session.commit()
