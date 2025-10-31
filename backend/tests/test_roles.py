from database.db import db
from database.models import Role


def get_access_token(client, email, password):
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_role(test_client, admin_user):
    import uuid

    token = get_access_token(test_client, admin_user.email, "adminpass")
    unique_name = f"NewRole_{uuid.uuid4().hex[:8]}"
    payload = {"name": unique_name, "description": "Created by test"}
    resp = test_client.post("/api/v1/roles/", json=payload, headers=auth_headers(token))
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == unique_name
    assert data["description"] == "Created by test"


def test_list_roles(test_client, admin_user):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    resp = test_client.get("/api/v1/roles/", headers=auth_headers(token))
    assert resp.status_code == 200
    assert isinstance(resp.json()["items"], list)


def test_get_role(test_client, admin_user, test_role):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    resp = test_client.get(f"/api/v1/roles/{test_role.id}", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == test_role.id
    assert data["name"] == test_role.name


def test_update_role(test_client, admin_user, test_role):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    update_payload = {"name": "UpdatedRole", "description": "Updated by test"}
    resp = test_client.put(f"/api/v1/roles/{test_role.id}", json=update_payload, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "UpdatedRole"
    assert data["description"] == "Updated by test"


def test_delete_role(test_client, admin_user, test_role):
    token = get_access_token(test_client, admin_user.email, "adminpass")
    resp = test_client.delete(f"/api/v1/roles/{test_role.id}", headers=auth_headers(token))
    assert resp.status_code == 204
    with db.get_session() as session:
        role = session.query(Role).filter_by(id=test_role.id).first()
        assert role is None
