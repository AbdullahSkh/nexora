"""Integration tests for the Authentication module.

Covers:
- POST /api/v1/auth/register  (new org creation, first user becomes admin)
- POST /api/v1/auth/register  (join existing org as regular user)
- POST /api/v1/auth/login
- POST /api/v1/auth/login     (wrong password)
- GET  /api/v1/users/me       (valid token)
- GET  /api/v1/users/me       (missing token → 401)
"""
import pytest

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/users/me"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _register(client, email="admin@acme.com", org="Acme Inc", password="Secret123!"):
    return await client.post(
        REGISTER_URL,
        json={
            "organization_name": org,
            "user_email": email,
            "password": password,
            "first_name": "Alice",
            "last_name": "Smith",
        },
    )


async def _login(client, email="admin@acme.com", password="Secret123!"):
    return await client.post(LOGIN_URL, json={"email": email, "password": password})


# ---------------------------------------------------------------------------
# Registration tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_register_new_org_creates_admin(async_client):
    """First user to register with a new org name becomes superuser."""
    resp = await _register(async_client)
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

    # Use the token to confirm is_superuser
    token = body["access_token"]
    me = await async_client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    data = me.json()
    assert data["is_superuser"] is True
    assert data["email"] == "admin@acme.com"


@pytest.mark.asyncio
async def test_register_second_user_same_org_is_not_admin(async_client):
    """Second registration with the same org name joins it as a regular user."""
    await _register(async_client)
    resp = await _register(async_client, email="bob@acme.com")
    assert resp.status_code == 200

    token = resp.json()["access_token"]
    me = await async_client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["is_superuser"] is False


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(async_client):
    await _register(async_client)
    resp = await _register(async_client)  # same email
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# Login tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_success(async_client):
    await _register(async_client)
    resp = await _login(async_client)
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(async_client):
    await _register(async_client)
    resp = await _login(async_client, password="WrongPassword!")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email_returns_401(async_client):
    resp = await _login(async_client, email="nobody@acme.com")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Protected endpoint tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_me_without_token_returns_401(async_client):
    resp = await async_client.get(ME_URL)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_with_invalid_token_returns_401(async_client):
    resp = await async_client.get(ME_URL, headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_auth_me_with_valid_token(async_client):
    reg_resp = await _register(async_client, email="auth_me_test@acme.com")
    token = reg_resp.json()["access_token"]
    resp = await async_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "auth_me_test@acme.com"
    assert data["is_superuser"] is True

