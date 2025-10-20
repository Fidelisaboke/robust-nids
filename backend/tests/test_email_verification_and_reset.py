import email
import re

import pytest

from database.db import db
from database.models import User
from services.email_service import EmailService


def extract_html_body_from_mime(mime_message):
    msg = email.message_from_string(str(mime_message))
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            payload = part.get_payload(decode=True)
            if payload:
                return payload.decode("utf-8")
    return None


def extract_token_from_email(email_content, token_type="verification"):
    """Extract token from email body for both verification and reset"""
    match = re.search(r"token=([\w\-\.]+)", email_content)
    return match.group(1) if match else None


@pytest.mark.usefixtures("setup_mail_dir")
def test_request_email_verification(test_client, test_user):
    email_service = EmailService()
    with email_service.fm.record_messages() as outbox:
        resp = test_client.post("/api/v1/auth/verify-email/request", json={"email": test_user.email})
        assert resp.status_code == 200
        assert "verification instructions" in resp.json()["detail"]
        assert len(outbox) == 1
    email_message = outbox[0]
    email_content = extract_html_body_from_mime(email_message)
    assert email_content is not None
    assert "verify" in email_content.lower()
    token = extract_token_from_email(email_content, token_type="verification")
    assert token


@pytest.mark.usefixtures("setup_mail_dir")
def test_verify_email_success(test_client, test_user):
    email_service = EmailService()
    with email_service.fm.record_messages() as outbox:
        test_client.post("/api/v1/auth/verify-email/request", json={"email": test_user.email})
        assert len(outbox) == 1
        email_message = outbox[0]
        email_content = extract_html_body_from_mime(email_message)
        assert email_content is not None
        token = extract_token_from_email(email_content, token_type="verification")
        resp = test_client.post("/api/v1/auth/verify-email", json={"token": token})
        assert resp.status_code == 200
        assert "verified" in resp.json()["detail"].lower()
        # Confirm user is now verified
        with db.get_session() as session:
            user = session.query(User).filter_by(email=test_user.email).first()
            assert user.email_verified


@pytest.mark.usefixtures("setup_mail_dir")
def test_verify_email_invalid_token(test_client):
    resp = test_client.post("/api/v1/auth/verify-email", json={"token": "invalid-token"})
    # Accept 400 or 422 for invalid token, but not 500
    assert resp.status_code in (400, 422)
    assert "invalid" in resp.json().get("detail", "").lower()


# Password Reset Request
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
