import bcrypt
import pytest
from fastapi.testclient import TestClient

from api.main import app
from database.db import db
from database.models import User

client = TestClient(app)


@pytest.fixture(scope='function')
def test_user():
    # Setup: create a test user in the test database using bcrypt
    password = 'password'
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with db.get_session() as session:
        user = User(
            email='test@example.com',
            password_hash=hashed,
            is_active=True,
            username='testuser',
        )
        session.add(user)
        session.commit()
        yield user
        # Teardown: remove the test user
        session.delete(user)
        session.commit()


def test_login_success(test_user):
    response = client.post('/api/v1/auth/login', json={'email': 'test@example.com', 'password': 'password'})
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert 'refresh_token' in data


def test_login_failure():
    response = client.post(
        '/api/v1/auth/login',
        json={'email': 'wrong@example.com', 'password': 'wrongpass'},
    )
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid email or password'
