"""Integration tests for the Marketing module."""
import pytest

REGISTER_URL = "/api/v1/auth/register"
MKT_BASE = "/api/v1/marketing"


async def _register_and_token(client, email="mkt@co.com", org="MktOrg", password="Pass123!"):
    resp = await client.post(
        REGISTER_URL,
        json={
            "organization_name": org,
            "user_email": email,
            "password": password,
            "first_name": "Market",
            "last_name": "Lead",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_campaign_and_lead_lifecycle(async_client):
    token = await _register_and_token(async_client, email="growth@co.com", org="GrowthOrg")

    # Create campaign
    camp_resp = await async_client.post(
        f"{MKT_BASE}/campaigns",
        json={
            "name": "Q4 SaaS Webinar",
            "type": "webinar",
            "budget": 5000.0,
            "status": "active",
        },
        headers=auth(token),
    )
    assert camp_resp.status_code == 201
    campaign = camp_resp.json()
    assert campaign["name"] == "Q4 SaaS Webinar"
    camp_id = campaign["id"]

    # Create lead associated with campaign
    lead_resp = await async_client.post(
        f"{MKT_BASE}/leads",
        json={
            "email": "prospect@enterprise.com",
            "first_name": "Bob",
            "last_name": "Prospect",
            "company": "Enterprise Inc",
            "campaign_id": camp_id,
            "score": 85,
        },
        headers=auth(token),
    )
    assert lead_resp.status_code == 201
    lead = lead_resp.json()
    assert lead["email"] == "prospect@enterprise.com"
    lead_id = lead["id"]

    # Update lead status to qualified
    patch_resp = await async_client.patch(
        f"{MKT_BASE}/leads/{lead_id}",
        json={"status": "qualified"},
        headers=auth(token),
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "qualified"

    # List leads filtering by campaign
    list_resp = await async_client.get(
        f"{MKT_BASE}/leads?campaign_id={camp_id}", headers=auth(token)
    )
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


@pytest.mark.asyncio
async def test_marketing_tenant_isolation(async_client):
    token_a = await _register_and_token(async_client, email="usera@mktorg1.com", org="MktOrg1")
    token_b = await _register_and_token(async_client, email="userb@mktorg2.com", org="MktOrg2")

    # Org 1 creates campaign
    c_resp = await async_client.post(
        f"{MKT_BASE}/campaigns",
        json={"name": "Org1 Secret Launch"},
        headers=auth(token_a),
    )
    assert c_resp.status_code == 201
    camp_id = c_resp.json()["id"]

    # Org 2 cannot read it
    get_resp = await async_client.get(f"{MKT_BASE}/campaigns/{camp_id}", headers=auth(token_b))
    assert get_resp.status_code == 404

    # Org 2 list is empty
    list_resp = await async_client.get(f"{MKT_BASE}/campaigns", headers=auth(token_b))
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 0
