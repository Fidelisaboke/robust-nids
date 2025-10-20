from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pyotp
import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.routers.mfa import limiter_by_user
from database.db import db
from database.models import User
from services.totp_service import totp_service

client = TestClient(app)


@pytest.mark.usefixtures("mfa_user")
def test_mfa_verify_success(mfa_user):
    # Step 1: Login to get challenge token
    login_resp = client.post("/api/v1/auth/login", json={"email": "mfa@example.com", "password": "mfapass"})
    assert login_resp.status_code == 200
    challenge_token = login_resp.json()["mfa_challenge_token"]

    # Step 2: Generate valid TOTP code
    totp = pyotp.TOTP(mfa_user.mfa_secret)
    code = totp.now()
    headers = {"Authorization": f"Bearer {challenge_token}"}
    verify_resp = client.post("/api/v1/auth/mfa/verify", json={"code": code}, headers=headers)
    assert verify_resp.status_code == 200
    data = verify_resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.usefixtures("mfa_user")
def test_mfa_verify_invalid_code(mfa_user):
    login_resp = client.post("/api/v1/auth/login", json={"email": "mfa@example.com", "password": "mfapass"})
    assert login_resp.status_code == 200
    challenge_token = login_resp.json()["mfa_challenge_token"]
    headers = {"Authorization": f"Bearer {challenge_token}"}
    resp = client.post("/api/v1/auth/mfa/verify", json={"code": "000000"}, headers=headers)
    assert resp.status_code == 400
    assert "Invalid MFA verification code" in resp.json().get("detail", "")


@pytest.mark.usefixtures("mfa_user")
def test_mfa_verify_rate_limit(mfa_user):
    # Reset rate limiter storage for this user before starting
    login_resp = client.post("/api/v1/auth/login", json={"email": "mfa@example.com", "password": "mfapass"})
    assert login_resp.status_code == 200
    challenge_token = login_resp.json()["mfa_challenge_token"]
    key = f"mfa-verify-{mfa_user.id}"
    try:
        limiter_by_user._storage.clear(key)
    except Exception:
        pass
    headers = {"Authorization": f"Bearer {challenge_token}"}
    limiter_by_user.enabled = True

    with patch("services.mfa_service.MFAService.verify_mfa_code", return_value=False):
        # First 3 requests: should not be rate limited
        for i in range(3):
            resp = client.post("/api/v1/auth/mfa/verify", json={"code": "000000"}, headers=headers)
            assert resp.status_code in (200, 400), (
                f"Unexpected status {resp.status_code} on request {i + 1} (should not be rate limited yet)"
            )
        # 4th and 5th requests: should be rate limited
        for i in range(2):
            resp = client.post("/api/v1/auth/mfa/verify", json={"code": "000000"}, headers=headers)
            assert resp.status_code == 429, (
                f"Expected 429 rate limit on request {4 + i}, got {resp.status_code}"
            )


@pytest.mark.usefixtures("mfa_user")
def test_mfa_verify_used_backup_code(mfa_user):
    # This patch directly disables the limiter instance for the 'with' block
    with patch.object(limiter_by_user, "enabled", False):
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "mfa@example.com", "password": "mfapass"}
        )
        assert login_resp.status_code == 200
        challenge_token = login_resp.json()["mfa_challenge_token"]

        backup_code = "CODE1-CODE2"  # A known, valid backup code matching the fixture
        headers = {"Authorization": f"Bearer {challenge_token}"}

        verify_resp = client.post("/api/v1/auth/mfa/verify", json={"code": backup_code}, headers=headers)

        assert verify_resp.status_code == 200
        data = verify_resp.json()
        assert "access_token" in data
        assert "refresh_token" in data


def test_mfa_enable_success(non_mfa_user):
    temp_secret = "JBSWY3DPEHPK3PXP"
    totp = pyotp.TOTP(temp_secret)
    code = totp.now()
    login_resp = client.post("/api/v1/auth/login", json={"email": non_mfa_user.email, "password": "nomfa"})
    access_token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = client.post(
        "/api/v1/auth/mfa/enable",
        json={"verification_code": code, "temp_secret": temp_secret},
        headers=headers,
    )
    assert resp.status_code == 200
    assert "backup_codes" in resp.json()


def test_mfa_disable_success(mfa_user):
    with patch.object(limiter_by_user, "enabled", False):
        # Login to get challenge token
        login_resp = client.post("/api/v1/auth/login", json={"email": mfa_user.email, "password": "mfapass"})
        assert login_resp.status_code == 200
        challenge_token = login_resp.json()["mfa_challenge_token"]

        totp = pyotp.TOTP(mfa_user.mfa_secret)
        code = totp.now()
        headers = {"Authorization": f"Bearer {challenge_token}"}
        verify_resp = client.post("/api/v1/auth/mfa/verify", json={"code": code}, headers=headers)
        assert verify_resp.status_code == 200
        access_token = verify_resp.json()["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}
        resp = client.post("/api/v1/auth/mfa/disable", json={"code": code}, headers=headers)
        assert resp.status_code == 200
        assert "MFA has been disabled" in resp.json().get("detail", "")


def test_mfa_disable_unauthorized(mfa_user):
    totp = pyotp.TOTP(mfa_user.mfa_secret)
    code = totp.now()
    resp = client.post("/api/v1/auth/mfa/disable", json={"code": code})
    assert resp.status_code == 403


def test_mfa_recovery_initiate_success(mfa_user):
    with patch("services.mfa_service.MFAService.initiate_mfa_recovery") as mock_recovery:
        mock_recovery.return_value = None
        resp = client.post("/api/v1/auth/mfa/recovery/initiate", json={"email": mfa_user.email})
        assert resp.status_code == 200
        assert "recovery link" in resp.json().get("detail", "")
        mock_recovery.assert_called()


def test_mfa_recovery_complete_success(mfa_user):
    with db.get_session() as session:
        user = session.merge(mfa_user)
        token = "valid-token-123"

        user.mfa_recovery_token = totp_service.hash_searchable_token(token)
        user.mfa_recovery_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        session.commit()
    resp = client.post("/api/v1/auth/mfa/recovery/complete", json={"mfa_recovery_token": token})
    assert resp.status_code == 200
    with db.get_session() as session:
        user = session.get(User, mfa_user.id)
        assert not user.mfa_enabled


def test_mfa_recovery_complete_invalid_token(mfa_user):
    resp = client.post("/api/v1/auth/mfa/recovery/complete", json={"mfa_recovery_token": "invalid-token"})
    assert resp.status_code == 400
    assert "Invalid or expired MFA recovery token" in resp.json().get("detail", "")


def test_admin_reset_mfa_success(mfa_user, admin_user):
    login_resp = client.post("/api/v1/auth/login", json={"email": admin_user.email, "password": "adminpass"})
    access_token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = client.post(f"/api/v1/users/{mfa_user.id}/reset-mfa", headers=headers)
    assert resp.status_code in (204, 200)
    with db.get_session() as session:
        user = session.get(User, mfa_user.id)
        assert not user.mfa_enabled


def test_admin_reset_mfa_non_admin_fails(non_mfa_user):
    login_resp = client.post("/api/v1/auth/login", json={"email": non_mfa_user.email, "password": "nomfa"})
    access_token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = client.post(f"/api/v1/users/{non_mfa_user.id}/reset-mfa", headers=headers)
    assert resp.status_code == 403
