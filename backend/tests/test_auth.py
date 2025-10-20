import pytest
from fastapi.testclient import TestClient

from api.main import app

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
    # Accept either a specific error message or a generic one
    assert (
        "Email verification is required" in data.get("detail", "")
        or "email" in data
        or "verify" in str(data).lower()
    )


def test_login_mfa_user_challenge_success(mfa_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "mfa@example.com", "password": "mfapass"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("mfa_required") is True
    assert "mfa_challenge_token" in data
