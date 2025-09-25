"""
Unit tests for AuthService user session lifecycle management.
"""

import uuid
from datetime import datetime, timedelta

import pytest

from database.models import User, UserSession
from services.auth import AuthService


class DummySession:
    def __init__(self):
        self.committed = False
        self.rolled_back = False
        self.added = []
        self.users = {}
        self.sessions = {}
        self.queries = []
        self._options = []
        self._order_by = None

    def query(self, model):
        self.queries.append(model)
        self._model = model
        return self

    def filter(self, *args, **kwargs):
        self._filters = args
        return self

    def options(self, *args, **kwargs):
        self._options.extend(args)
        return self

    def order_by(self, *args, **kwargs):
        self._order_by = args
        return self

    def first(self):
        if self._model == User:
            return self.users.get("first", None)
        elif self._model == UserSession:
            for s in self.sessions.values():
                if all([getattr(s, "is_active", True)]):
                    return s
            return None
        return None

    def all(self):
        if self._model == UserSession:
            return [s for s in self.sessions.values() if getattr(s, "is_active", True)]
        return list(self.users.values())

    def add(self, obj):
        self.added.append(obj)
        if isinstance(obj, User):
            if not hasattr(obj, "id") or obj.id is None:
                obj.id = len(self.added)
            self.users["first"] = obj
        elif isinstance(obj, UserSession):
            self.sessions[obj.id] = obj

    def flush(self):
        pass

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


def test_authenticate_creates_session(auth_service, dummy_db_factory):
    session = dummy_db_factory()
    auth_service.db_session_factory = lambda: session
    user = User(id=1, email="test@example.com", password_hash=b"$2b$12$abcdefghijklmno".decode(), is_active=True)
    session.users["first"] = user

    def fake_checkpw(pw, hashpw):
        return True

    import bcrypt

    bcrypt.checkpw = fake_checkpw
    result = auth_service.authenticate(
        "test@example.com", "password", device_info="Win10", ip_address="1.2.3.4", user_agent="TestAgent"
    )
    assert result["error"] is None
    assert result["user"]["id"] == 1
    assert result["session_id"] in session.sessions
    s = session.sessions[result["session_id"]]
    assert s.device_info == "Win10"
    assert s.ip_address == "1.2.3.4"
    assert s.user_agent == "TestAgent"
    assert s.is_active


def test_logout_user(auth_service, dummy_db_factory):
    session = dummy_db_factory()
    auth_service.db_session_factory = lambda: session
    user = User(id=2, email="logout@example.com", password_hash=b"$2b$12$abcdefghijklmno".decode(), is_active=True)
    session.users["first"] = user
    sid = str(uuid.uuid4())
    usession = UserSession(
        id=sid,
        user_id=2,
        device_info="Mac",
        ip_address="2.2.2.2",
        user_agent="Safari",
        login_time=datetime.now(),
        last_activity=datetime.now(),
        expires_at=datetime.now() + timedelta(hours=1),
        is_active=True,
    )
    session.sessions[sid] = usession
    result = auth_service.logout_user(2, sid)
    assert result
    assert not session.sessions[sid].is_active


def test_refresh_session(auth_service, dummy_db_factory):
    session = dummy_db_factory()
    auth_service.db_session_factory = lambda: session
    sid = str(uuid.uuid4())
    usession = UserSession(
        id=sid,
        user_id=3,
        device_info="Linux",
        ip_address="3.3.3.3",
        user_agent="Chrome",
        login_time=datetime.now(),
        last_activity=datetime.now(),
        expires_at=datetime.now() + timedelta(seconds=10),
        is_active=True,
    )
    session.sessions[sid] = usession
    result = auth_service.refresh_session(sid, extend_seconds=60)
    assert result
    assert session.sessions[sid].is_active
    assert session.sessions[sid].expires_at > datetime.now()
    # Expiry
    session.sessions[sid].expires_at = datetime.now() - timedelta(seconds=1)
    result2 = auth_service.refresh_session(sid, extend_seconds=60)
    assert not result2
    assert not session.sessions[sid].is_active


def test_invalidate_all_sessions(auth_service, dummy_db_factory):
    session = dummy_db_factory()
    auth_service.db_session_factory = lambda: session
    user_id = 4
    sids = [str(uuid.uuid4()) for _ in range(3)]
    for sid in sids:
        usession = UserSession(
            id=sid,
            user_id=user_id,
            device_info="dev",
            ip_address="4.4.4.4",
            user_agent="UA",
            login_time=datetime.now(),
            last_activity=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            is_active=True,
        )
        session.sessions[sid] = usession
    count = auth_service.invalidate_all_sessions(user_id)
    assert count == 3
    for sid in sids:
        assert not session.sessions[sid].is_active


def test_get_user_sessions_flags_current(auth_service, dummy_db_factory):
    session = dummy_db_factory()
    auth_service.db_session_factory = lambda: session
    user_id = 5
    sid1 = str(uuid.uuid4())
    sid2 = str(uuid.uuid4())
    usession1 = UserSession(
        id=sid1,
        user_id=user_id,
        device_info="dev1",
        ip_address="5.5.5.5",
        user_agent="UA1",
        login_time=datetime.now(),
        last_activity=datetime.now(),
        expires_at=datetime.now() + timedelta(hours=1),
        is_active=True,
    )
    usession2 = UserSession(
        id=sid2,
        user_id=user_id,
        device_info="dev2",
        ip_address="5.5.5.6",
        user_agent="UA2",
        login_time=datetime.now(),
        last_activity=datetime.now(),
        expires_at=datetime.now() + timedelta(hours=1),
        is_active=True,
    )
    session.sessions[sid1] = usession1
    session.sessions[sid2] = usession2
    sessions = auth_service.get_user_sessions(user_id, current_session_id=sid2)
    assert len(sessions) == 2
    for s in sessions:
        if s["id"] == sid2:
            assert s["is_current"]
        else:
            assert not s["is_current"]
    # Expiry enforcement
    session.sessions[sid1].expires_at = datetime.now() - timedelta(seconds=1)
    sessions2 = auth_service.get_user_sessions(user_id, current_session_id=sid2)
    assert len(sessions2) == 1
    assert sessions2[0]["id"] == sid2
    assert sessions2[0]["is_current"]
