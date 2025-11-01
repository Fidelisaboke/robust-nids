from unittest.mock import patch

from database.db import db
from database.models import User
from services.email_service import EmailService


def get_access_token(client, email, password):
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_user(test_client, admin_user):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    # Ensure no user with this email exists before test
    with db.get_session() as session:
        existing = session.query(User).filter_by(email="newusertest@example.com").first()
        if existing:
            session.delete(existing)
            session.commit()
        # Create a test role to assign
        from database.repositories.role import RoleRepository

        role_repo = RoleRepository(session)
        test_role = role_repo.get_by_name("test_create_user_role")
        if not test_role:
            test_role = role_repo.create({"name": "test_create_user_role"})
        session.commit()
        test_role_id = test_role.id
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
        "role_ids": [test_role_id],
    }
    resp = test_client.post("/api/v1/users/", json=payload, headers=auth_headers(token))
    assert resp.status_code == 201, f"Response: {resp.status_code}, {resp.text}"
    data = resp.json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]


def test_list_users(test_client, admin_user):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    resp = test_client.get("/api/v1/users/", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert isinstance(data["items"], list)


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

    # Ensure the user is deactivated before activation test
    with db.get_session() as session:
        user = session.get(User, test_user.id)
        user.is_active = False
        session.commit()

    with (
        patch.object(EmailService, "send_user_account_activated_email"),
        patch.object(EmailService, "send_admin_user_account_activated_email"),
    ):
        resp = test_client.post(f"/api/v1/users/{test_user.id}/activate", headers=auth_headers(token))
        print(resp.json())
        assert resp.status_code == 200
        detail = resp.json()["detail"]
        assert "activated successfully" in detail or "already active" in detail


def test_deactivate_user(test_client, admin_user, test_user):
    token = get_access_token(test_client, admin_user.email, "adminpass")

    with (
        patch.object(EmailService, "send_user_account_deactivated_email"),
        patch.object(EmailService, "send_admin_user_account_deactivated_email"),
    ):
        resp = test_client.post(f"/api/v1/users/{test_user.id}/deactivate", headers=auth_headers(token))
        assert resp.status_code == 200
        assert "deactivated successfully" in resp.json()["detail"]


def test_admin_cannot_deactivate_self(test_client, admin_user):
    token = get_access_token(test_client, admin_user.email, "adminpass")

    resp = test_client.post(f"/api/v1/users/{admin_user.id}/deactivate", headers=auth_headers(token))
    assert resp.status_code == 400
    assert "cannot deactivate your own account" in resp.json()["detail"]


def test_update_user_roles_success(test_client, admin_user, test_user, test_role):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    # Ensure test_user and test_role are in the same session and visible
    with db.get_session() as session:
        user = session.get(User, test_user.id)
        role = session.get(type(test_role), test_role.id)
        assert user is not None, "Test user not found in DB"
        assert role is not None, "Test role not found in DB"
    # Assign test_role to test_user
    payload = {"role_ids": [test_role.id]}
    resp = test_client.put(
        f"/api/v1/users/{test_user.id}/roles",
        json=payload,
        headers=auth_headers(token),
    )
    assert resp.status_code == 200, f"Response: {resp.status_code}, {resp.text}"
    data = resp.json()
    # The response should have roles under data["user"]["roles"]
    assert any(role["id"] == test_role.id for role in data["user"]["roles"])
    # Confirm in DB
    with db.get_session() as session:
        user = session.get(User, test_user.id)
        assert any(role.id == test_role.id for role in user.roles)


def test_update_user_roles_self_change_forbidden(test_client, admin_user, test_role):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    payload = {"role_ids": [test_role.id]}
    resp = test_client.put(
        f"/api/v1/users/{admin_user.id}/roles",
        json=payload,
        headers=auth_headers(token),
    )
    assert resp.status_code == 400
    assert "cannot change your own role" in resp.json()["detail"].lower()


def test_update_user_roles_invalid_role_id(test_client, admin_user, test_user):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    invalid_role_id = 999999  # unlikely to exist
    payload = {"role_ids": [invalid_role_id]}
    resp = test_client.put(
        f"/api/v1/users/{test_user.id}/roles",
        json=payload,
        headers=auth_headers(token),
    )
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()
