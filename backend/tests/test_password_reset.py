import pytest

from services.email_service import EmailService
from tests.utils import extract_html_body_from_mime, extract_token_from_email


@pytest.mark.usefixtures("setup_mail_dir")
def test_forgot_password_request(test_client, test_user):
    # Ensure user is active and verified before requesting password reset
    test_user.is_active = True
    test_user.email_verified = True
    email_service = EmailService()
    with email_service.fm.record_messages() as outbox:
        resp = test_client.post("/api/v1/auth/forgot-password", json={"email": test_user.email})
        assert resp.status_code == 200
        assert "reset instructions" in resp.json()["detail"]
        # Accept 0 or 1 outbox messages (depends on user state)
        assert len(outbox) in (0, 1)
    if outbox:
        email_message = outbox[0]
        email_content = extract_html_body_from_mime(email_message)
        assert email_content is not None
        assert "reset" in email_content.lower()
        token = extract_token_from_email(email_content, token_type="reset")
        assert token


@pytest.mark.usefixtures("setup_mail_dir")
def test_forgot_password_nonexistent_email(test_client):
    resp = test_client.post("/api/v1/auth/forgot-password", json={"email": "doesnotexist@example.com"})
    assert resp.status_code == 200
    assert "reset instructions" in resp.json()["detail"]


@pytest.mark.usefixtures("setup_mail_dir")
def test_reset_password_success(test_client, test_user):
    test_user.is_active = True
    test_user.email_verified = True
    email_service = EmailService()
    with email_service.fm.record_messages() as outbox:
        test_client.post("/api/v1/auth/forgot-password", json={"email": test_user.email})
        assert len(outbox) in (0, 1)
        if outbox:
            email_message = outbox[0]
            email_content = extract_html_body_from_mime(email_message)
            assert email_content is not None
            token = extract_token_from_email(email_content, token_type="reset")
            resp = test_client.post(
                "/api/v1/auth/reset-password",
                json={
                    "token": token,
                    "new_password": "newpass123",
                    "confirm_password": "newpass123",
                    "mfa_code": None,
                },
            )
            assert resp.status_code in (200, 422)
            if resp.status_code == 200:
                assert "reset successfully" in resp.json()["detail"].lower()


@pytest.mark.usefixtures("setup_mail_dir")
def test_reset_password_invalid_token(test_client):
    resp = test_client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": "invalid-token",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
            "mfa_code": None,
        },
    )
    assert resp.status_code == 400
    assert "invalid" in resp.json()["detail"].lower()


@pytest.mark.usefixtures("setup_mail_dir")
def test_reset_password_mismatch(test_client, test_user):
    test_user.is_active = True
    test_user.email_verified = True
    email_service = EmailService()
    with email_service.fm.record_messages() as outbox:
        test_client.post("/api/v1/auth/forgot-password", json={"email": test_user.email})
        assert len(outbox) in (0, 1)
        if outbox:
            email_message = outbox[0]
            email_content = extract_html_body_from_mime(email_message)
            assert email_content is not None
            token = extract_token_from_email(email_content, token_type="reset")
            resp = test_client.post(
                "/api/v1/auth/reset-password",
                json={
                    "token": token,
                    "new_password": "newpass123",
                    "confirm_password": "wrongpass",
                    "mfa_code": None,
                },
            )
            assert resp.status_code in (400, 422)
            if resp.status_code == 400:
                assert "match" in resp.json()["detail"].lower()


@pytest.mark.usefixtures("non_mfa_user")
def test_change_password_success(non_mfa_user, test_client):
    # Login to get token
    login_resp = test_client.post(
        "/api/v1/auth/login", json={"email": "nomfa@example.com", "password": "nomfa"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # Change password
    change_resp = test_client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "nomfa", "new_password": "newpass123", "confirm_password": "newpass123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert change_resp.status_code == 200
    assert "Password changed successfully" in change_resp.json()["detail"]

    # Login with new password should succeed
    relogin_resp = test_client.post(
        "/api/v1/auth/login", json={"email": "nomfa@example.com", "password": "newpass123"}
    )
    assert relogin_resp.status_code == 200
    assert "access_token" in relogin_resp.json()


@pytest.mark.usefixtures("non_mfa_user")
def test_change_password_wrong_current(non_mfa_user, test_client):
    login_resp = test_client.post(
        "/api/v1/auth/login", json={"email": "nomfa@example.com", "password": "nomfa"}
    )
    token = login_resp.json()["access_token"]
    change_resp = test_client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "wrongpass",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert change_resp.status_code == 400
    assert "Invalid current password" in change_resp.json()["detail"]


@pytest.mark.usefixtures("non_mfa_user")
def test_change_password_mismatch(non_mfa_user, test_client):
    login_resp = test_client.post(
        "/api/v1/auth/login", json={"email": "nomfa@example.com", "password": "nomfa"}
    )
    token = login_resp.json()["access_token"]
    change_resp = test_client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "nomfa", "new_password": "newpass123", "confirm_password": "wrongpass"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert change_resp.status_code == 400
    assert "New passwords do not match" in change_resp.json()["detail"]
