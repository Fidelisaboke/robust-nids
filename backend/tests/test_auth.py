import pytest
from fastapi.testclient import TestClient

from api.main import app
from database.db import db
from database.models import User
from services.email_service import EmailService

client = TestClient(app)


@pytest.mark.usefixtures("non_mfa_user")
def test_login_success(non_mfa_user):
    response = client.post("/api/v1/auth/login", json={"email": "nomfa@example.com", "password": "nomfa"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_failure():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_nonexistent_user():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_unverified_email(unverified_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "unverified@example.com", "password": "unverified"},
    )
    assert response.status_code == 200
    data = response.json()

    # Check for the specific structure expected for unverified emails
    assert "email_verified" in data
    assert data["email_verified"] is False
    assert "email" in data
    assert data["email"] == "unverified@example.com"


def test_login_mfa_user_challenge_success(mfa_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "mfa@example.com", "password": "mfapass"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("mfa_required") is True
    assert "mfa_challenge_token" in data


@pytest.mark.usefixtures("setup_mail_dir")
def test_register_user_success(test_client):
    # Ensure no user with this email exists before test
    with db.get_session() as session:
        existing = session.query(User).filter_by(email="testregister@example.com").first()
        if existing:
            session.delete(existing)
            session.commit()
    payload = {
        "email": "testregister@example.com",
        "username": "testregister",
        "first_name": "New",
        "last_name": "User",
        "password": "newuserpass123",
        "confirm_password": "newuserpass123",
        "phone": "1234567890",
        "department": "IT",
        "job_title": "Engineer",
    }
    email_service = EmailService()
    with email_service.fm.record_messages() as outbox:
        resp = test_client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == payload["email"]
        assert data["username"] == payload["username"]
        # Should send two emails: user confirmation and admin notification
        assert len(outbox) == 2
    with db.get_session() as session:
        user = session.query(User).filter_by(email=payload["email"]).first()
        assert user is not None
        assert user.username == payload["username"]


@pytest.mark.usefixtures("setup_mail_dir")
def test_register_user_duplicate_email(test_user):
    payload = {
        "email": test_user.email,
        "username": "anotheruser",
        "first_name": "Another",
        "last_name": "User",
        "password": "anotherpass123",
        "confirm_password": "anotherpass123",
        "phone": "1234567890",
        "department": "IT",
        "job_title": "Engineer",
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 400
    assert "already" in resp.json()["detail"].lower()


@pytest.mark.usefixtures("setup_mail_dir")
def test_register_user_missing_fields():
    payload = {
        "email": "incomplete@example.com",
        # Missing username, first_name, last_name, password
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422
    assert "field required" in str(resp.json()).lower()


def test_refresh_token_success(non_mfa_user):
    # Login to get refresh token
    response = client.post(
        "/api/v1/auth/login",
        json={"email": non_mfa_user.email, "password": "nomfa"},
    )
    assert response.status_code == 200
    data = response.json()
    refresh_token = data["refresh_token"]
    # Use refresh token to get new access token
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens
    assert tokens["refresh_token"] == refresh_token


def test_refresh_token_invalid():
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalidtoken"})
    assert resp.status_code == 401
    assert "invalid or expired" in resp.json()["detail"].lower()


def test_read_profile_success(non_mfa_user):
    # Login to get access token
    response = client.post(
        "/api/v1/auth/login",
        json={"email": non_mfa_user.email, "password": "nomfa"},
    )
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = client.get("/api/v1/auth/users/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == non_mfa_user.email
    assert data["username"] == non_mfa_user.username


def test_read_profile_unauthorized():
    resp = client.get("/api/v1/auth/users/me")
    assert resp.status_code == 401 or resp.status_code == 403
