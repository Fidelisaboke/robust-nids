from services.email_service import EmailService


def get_access_token(client, email, password):
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_user(test_client, admin_user):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    payload = {
        "email": "newusertest@example.com",
        "username": "newusertest",
        "password": "newusertestpass123",
        "first_name": "New",
        "last_name": "User",
        "phone": "1234567890",
        "department": "IT",
        "job_title": "Engineer",
        "is_active": True,
        "roles": [admin_user.roles[0].id] if admin_user.roles else [],
    }
    resp = test_client.post("/api/v1/users/", json=payload, headers=auth_headers(token))
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]


def test_list_users(test_client, admin_user):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    resp = test_client.get("/api/v1/users/", headers=auth_headers(token))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_user(test_client, admin_user, test_user):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    resp = test_client.get(f"/api/v1/users/{test_user.id}", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == test_user.email
    assert data["username"] == test_user.username


def test_update_user(test_client, admin_user, test_user):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    update_payload = {"first_name": "Updated", "last_name": "User"}
    resp = test_client.put(f"/api/v1/users/{test_user.id}", json=update_payload, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "User"


def test_delete_user(test_client, admin_user):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    payload = {
        "email": "deleteuser@example.com",
        "username": "deleteuser",
        "first_name": "Delete",
        "last_name": "User",
        "password": "deletepass123",
        "confirm_password": "deletepass123",
        "phone": "1234567890",
        "department": "IT",
        "job_title": "Engineer",
    }
    test_client.post("/api/v1/auth/register", json=payload)
    from database.db import db
    from database.models import User

    with db.get_session() as session:
        user = session.query(User).filter_by(email=payload["email"]).first()
        user_id = user.id
    resp = test_client.delete(f"/api/v1/users/{user_id}", headers=auth_headers(token))
    assert resp.status_code == 204
    with db.get_session() as session:
        user = session.query(User).filter_by(email=payload["email"]).first()
        assert user is None


def test_admin_reset_user_mfa(test_client, admin_user, test_user):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    resp = test_client.post(f"/api/v1/users/{test_user.id}/reset-mfa", headers=auth_headers(token))
    assert resp.status_code == 200
    assert "MFA has been reset" in resp.json()["detail"]


def test_activate_user(test_client, admin_user, test_user):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    from unittest.mock import patch

    with (
        patch.object(EmailService, "send_user_account_activated_email"),
        patch.object(EmailService, "send_admin_user_account_activated_email"),
    ):
        resp = test_client.post(f"/api/v1/users/{test_user.id}/activate", headers=auth_headers(token))
        assert resp.status_code == 200
        detail = resp.json()["detail"]
        assert "activated successfully" in detail or "already active" in detail


def test_deactivate_user(test_client, admin_user, test_user):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    from unittest.mock import patch

    with (
        patch.object(EmailService, "send_user_account_deactivated_email"),
        patch.object(EmailService, "send_admin_user_account_deactivated_email"),
    ):
        resp = test_client.post(f"/api/v1/users/{test_user.id}/deactivate", headers=auth_headers(token))
        assert resp.status_code == 200
        assert "deactivated successfully" in resp.json()["detail"]
