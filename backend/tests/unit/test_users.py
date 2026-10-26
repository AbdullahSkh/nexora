"""Integration tests for the Users (team management) module.

Covers:
- GET  /api/v1/users/          (list team members, admin only)
- POST /api/v1/users/          (create team member, admin only)
- PATCH /api/v1/users/{id}     (update team member, admin only)
- DELETE /api/v1/users/{id}    (deactivate team member, admin only)
- Non-admin gets 403 on privileged endpoints
"""
import pytest

REGISTER_URL = "/api/v1/auth/register"
USERS_URL = "/api/v1/users"
ME_URL = "/api/v1/users/me"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def register_and_login(client, email, org="Acme Inc", password="Secret123!"):
    resp = await client.post(
        REGISTER_URL,
        json={"organization_name": org, "user_email": email, "password": password, "first_name": "Test", "last_name": "User"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# List team members
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_admin_can_list_team_members(async_client):
    admin_token = await register_and_login(async_client, "admin@acme.com")
    resp = await async_client.get(f"{USERS_URL}/", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    members = resp.json()
    assert isinstance(members, list)
    assert len(members) == 1  # just the admin


@pytest.mark.asyncio
async def test_non_admin_cannot_list_team_members(async_client):
    await register_and_login(async_client, "admin@acme.com")
    regular_token = await register_and_login(async_client, "user@acme.com")
    resp = await async_client.get(f"{USERS_URL}/", headers=auth_headers(regular_token))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Create team member (POST /users/)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_admin_can_add_team_member(async_client):
    admin_token = await register_and_login(async_client, "admin@acme.com")
    resp = await async_client.post(
        f"{USERS_URL}/",
        json={"email": "newbie@acme.com", "password": "Pass123!", "first_name": "New", "last_name": "Hire"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "newbie@acme.com"
    assert data["is_superuser"] is False


@pytest.mark.asyncio
async def test_non_admin_cannot_add_team_member(async_client):
    await register_and_login(async_client, "admin@acme.com")
    regular_token = await register_and_login(async_client, "regular@acme.com")
    resp = await async_client.post(
        f"{USERS_URL}/",
        json={"email": "newbie@acme.com", "password": "Pass123!"},
        headers=auth_headers(regular_token),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_add_duplicate_team_member_returns_409(async_client):
    admin_token = await register_and_login(async_client, "admin@acme.com")
    await async_client.post(
        f"{USERS_URL}/",
        json={"email": "dup@acme.com", "password": "Pass123!"},
        headers=auth_headers(admin_token),
    )
    resp = await async_client.post(
        f"{USERS_URL}/",
        json={"email": "dup@acme.com", "password": "Pass123!"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# Update team member
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_admin_can_update_team_member(async_client):
    admin_token = await register_and_login(async_client, "admin@acme.com")
    create_resp = await async_client.post(
        f"{USERS_URL}/",
        json={"email": "member@acme.com", "password": "Pass123!", "first_name": "Old"},
        headers=auth_headers(admin_token),
    )
    user_id = create_resp.json()["id"]

    resp = await async_client.patch(
        f"{USERS_URL}/{user_id}",
        json={"first_name": "Updated"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "Updated"


# ---------------------------------------------------------------------------
# Deactivate team member
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_admin_can_deactivate_team_member(async_client):
    admin_token = await register_and_login(async_client, "admin@acme.com")
    create_resp = await async_client.post(
        f"{USERS_URL}/",
        json={"email": "leaver@acme.com", "password": "Pass123!"},
        headers=auth_headers(admin_token),
    )
    user_id = create_resp.json()["id"]

    resp = await async_client.delete(f"{USERS_URL}/{user_id}", headers=auth_headers(admin_token))
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_admin_cannot_deactivate_self(async_client):
    admin_token = await register_and_login(async_client, "admin@acme.com")
    me = await async_client.get(ME_URL, headers=auth_headers(admin_token))
    admin_id = me.json()["id"]

    resp = await async_client.delete(f"{USERS_URL}/{admin_id}", headers=auth_headers(admin_token))
    assert resp.status_code == 400
