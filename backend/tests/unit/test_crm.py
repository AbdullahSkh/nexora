"""Integration tests for the CRM module.

Covers Companies, Contacts, Deals, and Activities CRUD + org-isolation.
"""
import pytest

REGISTER_URL = "/api/v1/auth/register"
CRM_BASE = "/api/v1/crm"


async def _register_and_token(client, email="admin@co.com", org="MyOrg", password="Pass123!"):
    resp = await client.post(
        REGISTER_URL,
        json={"organization_name": org, "user_email": email, "password": password,
              "first_name": "A", "last_name": "B"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_and_list_companies(async_client):
    token = await _register_and_token(async_client)
    resp = await async_client.post(
        f"{CRM_BASE}/companies",
        json={"name": "Acme Corp", "industry": "SaaS"},
        headers=auth(token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Acme Corp"

    list_resp = await async_client.get(f"{CRM_BASE}/companies", headers=auth(token))
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


@pytest.mark.asyncio
async def test_update_company(async_client):
    token = await _register_and_token(async_client)
    create_resp = await async_client.post(
        f"{CRM_BASE}/companies",
        json={"name": "OldName"},
        headers=auth(token),
    )
    cid = create_resp.json()["id"]
    resp = await async_client.patch(
        f"{CRM_BASE}/companies/{cid}",
        json={"name": "NewName"},
        headers=auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "NewName"


@pytest.mark.asyncio
async def test_delete_company(async_client):
    token = await _register_and_token(async_client)
    create_resp = await async_client.post(
        f"{CRM_BASE}/companies", json={"name": "ToBeDel"}, headers=auth(token)
    )
    cid = create_resp.json()["id"]
    del_resp = await async_client.delete(f"{CRM_BASE}/companies/{cid}", headers=auth(token))
    assert del_resp.status_code == 204

    get_resp = await async_client.get(f"{CRM_BASE}/companies/{cid}", headers=auth(token))
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_company_not_visible_cross_org(async_client):
    """A company from org A should return 404 for a user in org B."""
    token_a = await _register_and_token(async_client, "a@a.com", "OrgA")
    token_b = await _register_and_token(async_client, "b@b.com", "OrgB")
    create_resp = await async_client.post(
        f"{CRM_BASE}/companies", json={"name": "OrgA Corp"}, headers=auth(token_a)
    )
    cid = create_resp.json()["id"]
    resp = await async_client.get(f"{CRM_BASE}/companies/{cid}", headers=auth(token_b))
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_and_get_contact(async_client):
    token = await _register_and_token(async_client)
    resp = await async_client.post(
        f"{CRM_BASE}/contacts",
        json={"first_name": "John", "last_name": "Doe", "email": "john@acme.com"},
        headers=auth(token),
    )
    assert resp.status_code == 201
    cid = resp.json()["id"]
    get_resp = await async_client.get(f"{CRM_BASE}/contacts/{cid}", headers=auth(token))
    assert get_resp.status_code == 200
    assert get_resp.json()["email"] == "john@acme.com"


# ---------------------------------------------------------------------------
# Deals
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_deal_and_filter_by_stage(async_client):
    token = await _register_and_token(async_client)
    await async_client.post(
        f"{CRM_BASE}/deals",
        json={"title": "Big Deal", "stage": "lead", "value": "50000.00"},
        headers=auth(token),
    )
    await async_client.post(
        f"{CRM_BASE}/deals",
        json={"title": "Small Deal", "stage": "qualified"},
        headers=auth(token),
    )

    all_resp = await async_client.get(f"{CRM_BASE}/deals", headers=auth(token))
    assert len(all_resp.json()) == 2

    filtered_resp = await async_client.get(
        f"{CRM_BASE}/deals?stage=lead", headers=auth(token)
    )
    assert len(filtered_resp.json()) == 1
    assert filtered_resp.json()[0]["title"] == "Big Deal"


@pytest.mark.asyncio
async def test_update_deal_stage(async_client):
    token = await _register_and_token(async_client)
    create_resp = await async_client.post(
        f"{CRM_BASE}/deals",
        json={"title": "Pipeline Deal", "stage": "lead"},
        headers=auth(token),
    )
    did = create_resp.json()["id"]
    resp = await async_client.patch(
        f"{CRM_BASE}/deals/{did}",
        json={"stage": "proposal"},
        headers=auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["stage"] == "proposal"


# ---------------------------------------------------------------------------
# Activities
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_and_list_activities(async_client):
    token = await _register_and_token(async_client)
    resp = await async_client.post(
        f"{CRM_BASE}/activities",
        json={"type": "call", "subject": "Intro call"},
        headers=auth(token),
    )
    assert resp.status_code == 201
    assert resp.json()["subject"] == "Intro call"

    list_resp = await async_client.get(f"{CRM_BASE}/activities", headers=auth(token))
    assert len(list_resp.json()) == 1


@pytest.mark.asyncio
async def test_activity_requires_auth(async_client):
    resp = await async_client.get(f"{CRM_BASE}/activities")
    assert resp.status_code == 401
