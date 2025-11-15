import pytest

from database.db import db
from database.models import User
from services.email_service import EmailService
from tests.utils import extract_html_body_from_mime, extract_token_from_email


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
