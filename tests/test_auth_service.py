"""
Unit tests for AuthService (refactored).
"""

import pytest

from database.models import User
from services.auth import AuthService


class DummySession:
    def __init__(self):
        self.committed = False
        self.rolled_back = False
        self.added = []
        self.users = {}
        self.queries = []
        self._options = []
        self._order_by = None

    def query(self, model):
        self.queries.append(model)
        return self

    def filter(self, *args, **kwargs):
        return self

    def options(self, *args, **kwargs):
        self._options.extend(args)
        return self

    def order_by(self, *args, **kwargs):
        self._order_by = args
        return self

    def first(self):
        return self.users.get("first", None)

    def all(self):
        return list(self.users.values())

    def add(self, obj):
        self.added.append(obj)
        # Simulate DB auto-increment ID
        if not hasattr(obj, "id") or obj.id is None:
            obj.id = len(self.added)
        self.users["first"] = obj

    def flush(self):
        # Ensure user has ID after flush
        if self.added:
            for obj in self.added:
                if not hasattr(obj, "id") or obj.id is None:
                    obj.id = len(self.added)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


@pytest.fixture
def dummy_db_factory():
    def factory():
        return DummySession()

    return factory


@pytest.fixture
def auth_service(dummy_db_factory):
    return AuthService(dummy_db_factory)


def test_create_user_success(auth_service, dummy_db_factory):
    session = dummy_db_factory()
    auth_service.db_session_factory = lambda: session
    email = "test@example.com"
    password = "password123"
    first_name = "Test"
    last_name = "User"
    username = "testuser"
    department = "IT"
    session.users["first"] = None
    user_id = auth_service.create_user(email, password, first_name, last_name, username, department)
    assert user_id is not None
    assert session.added


def test_create_user_duplicate(auth_service, dummy_db_factory):
    session = dummy_db_factory()
    auth_service.db_session_factory = lambda: session
    session.users["first"] = User()
    with pytest.raises(ValueError):
        auth_service.create_user("test@example.com", "password", "Test", "User", "testuser", "IT")


def test_authenticate_invalid(auth_service, dummy_db_factory):
    session = dummy_db_factory()
    auth_service.db_session_factory = lambda: session
    session.users["first"] = None
    user, msg = auth_service.authenticate("bad@example.com", "badpass")
    assert user is None
    assert msg == "Invalid credentials."


def test_enable_disable_mfa(auth_service, dummy_db_factory):
    session = dummy_db_factory()
    auth_service.db_session_factory = lambda: session
    user = User(id=1)
    session.users["first"] = user
    result = auth_service.enable_mfa("SECRET", 1)
    assert result["success"]
    assert user.mfa_enabled
    assert user.mfa_secret == "SECRET"
    assert user.mfa_backup_codes
    assert len(user.mfa_backup_codes) == 10
    assert session.committed
    # Disable
    session.committed = False
    result2 = auth_service.disable_mfa(1)
    assert result2 is True
    assert not user.mfa_enabled
    assert user.mfa_secret is None
    assert session.committed


def test_generate_new_backup_codes(auth_service, dummy_db_factory):
    session = dummy_db_factory()
    auth_service.db_session_factory = lambda: session
    user = User(id=2)
    session.users["first"] = user
    result = auth_service.generate_new_backup_codes(2)
    assert result["success"]
    assert len(user.mfa_backup_codes) == 10
    assert session.committed


def test_update_user_profile(auth_service, dummy_db_factory):
    session = dummy_db_factory()
    auth_service.db_session_factory = lambda: session
    user = User(id=3, first_name="Old", last_name="Name", email="old@example.com", preferences=None)
    session.users["first"] = user
    update_data = {"first_name": "New", "last_name": "Name", "preferences": {"theme": "dark"}}
    result = auth_service.update_user_profile(3, update_data)
    assert result is True
    assert user.first_name == "New"
    assert user.preferences["theme"] == "dark"
    assert session.committed is True


def test_update_user_preferences(auth_service, dummy_db_factory):
    session = dummy_db_factory()
    auth_service.db_session_factory = lambda: session
    user = User(id=4, preferences={"theme": "light"})
    session.users["first"] = user
    result = auth_service.update_user_preferences(4, {"theme": "dark"})
    assert result is True
    assert user.preferences["theme"] == "dark"
    assert session.committed is True


def test_get_user_by_id(auth_service, dummy_db_factory):
    session = dummy_db_factory()
    auth_service.db_session_factory = lambda: session
    user = User(id=5)
    session.users["first"] = user
    result = auth_service.get_user_by_id(5)
    assert result == user


def test_get_user_profile(auth_service, dummy_db_factory):
    session = dummy_db_factory()
    auth_service.db_session_factory = lambda: session
    user = User(id=6, email="profile@example.com", first_name="Prof", last_name="Ile", username="prof", preferences={})
    session.users["first"] = user
    result = auth_service.get_user_profile(6)
    assert result["email"] == "profile@example.com"
    assert result["first_name"] == "Prof"
    assert result["username"] == "prof"


def test_get_all_users(auth_service, dummy_db_factory):
    session = dummy_db_factory()
    auth_service.db_session_factory = lambda: session
    user1 = User(id=7)
    user2 = User(id=8)
    session.users = {"first": user1, "second": user2}
    result = auth_service.get_all_users()
    assert user1 in result and user2 in result
