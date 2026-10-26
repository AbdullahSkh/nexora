"""Integration tests for the Analytics module."""
import pytest

REGISTER_URL = "/api/v1/auth/register"
ANALYTICS_BASE = "/api/v1/analytics"


async def _register_and_token(client, email="analytics@co.com", org="MetricsOrg", password="Pass123!"):
    resp = await client.post(
        REGISTER_URL,
        json={
            "organization_name": org,
            "user_email": email,
            "password": password,
            "first_name": "Data",
            "last_name": "Analyst",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_analytics_overview_and_breakdowns(async_client):
    token = await _register_and_token(async_client, email="exec@corp.com", org="CorpOrg")

    # 1. Overview metrics
    overview_resp = await async_client.get(f"{ANALYTICS_BASE}/overview", headers=auth(token))
    assert overview_resp.status_code == 200
    overview = overview_resp.json()
    assert "total_revenue" in overview
    assert "active_projects" in overview
    assert "pipeline_value" in overview
    assert "open_tickets_count" in overview

    # 2. CRM metrics
    crm_resp = await async_client.get(f"{ANALYTICS_BASE}/crm", headers=auth(token))
    assert crm_resp.status_code == 200
    crm = crm_resp.json()
    assert "deals_by_stage" in crm
    assert "pipeline_value" in crm
    assert "total_contacts" in crm

    # 3. Projects metrics
    proj_resp = await async_client.get(f"{ANALYTICS_BASE}/projects", headers=auth(token))
    assert proj_resp.status_code == 200
    projects = proj_resp.json()
    assert "tasks_by_status" in projects
    assert "active_projects_count" in projects

    # 4. Finance metrics
    fin_resp = await async_client.get(f"{ANALYTICS_BASE}/finance", headers=auth(token))
    assert fin_resp.status_code == 200
    fin = fin_resp.json()
    assert "total_invoiced" in fin
    assert "total_paid" in fin
    assert "total_expenses" in fin
