"""Integration tests for the Support module.

Covers Tickets, Comments, Status updates, and Multi-tenancy isolation.
"""
import pytest

REGISTER_URL = "/api/v1/auth/register"
SUPPORT_BASE = "/api/v1/support"


async def _register_and_token(client, email="support@co.com", org="SupportOrg", password="Pass123!"):
    resp = await client.post(
        REGISTER_URL,
        json={
            "organization_name": org,
            "user_email": email,
            "password": password,
            "first_name": "Support",
            "last_name": "Agent",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_and_detail_ticket(async_client):
    token = await _register_and_token(async_client, email="agent1@co.com", org="HelpdeskOrg")

    ticket_data = {
        "customer_email": "customer@client.com",
        "customer_name": "Alice Customer",
        "subject": "Cannot export invoices to PDF",
        "description": "Getting a 500 server error when clicking export.",
        "priority": "high",
    }

    create_resp = await async_client.post(
        f"{SUPPORT_BASE}/",
        json=ticket_data,
        headers=auth(token),
    )
    assert create_resp.status_code == 201
    ticket = create_resp.json()
    assert ticket["subject"] == "Cannot export invoices to PDF"
    assert ticket["status"] == "open"
    ticket_id = ticket["id"]

    # Add comment
    comment_resp = await async_client.post(
        f"{SUPPORT_BASE}/{ticket_id}/comments",
        json={"body": "Investigating PDF generation service.", "is_internal": True},
        headers=auth(token),
    )
    assert comment_resp.status_code == 201
    assert comment_resp.json()["is_internal"] is True

    # Get ticket detail with comments
    detail_resp = await async_client.get(f"{SUPPORT_BASE}/{ticket_id}", headers=auth(token))
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert len(detail["comments"]) == 1
    assert detail["comments"][0]["body"] == "Investigating PDF generation service."

    # Update ticket status to resolved
    patch_resp = await async_client.patch(
        f"{SUPPORT_BASE}/{ticket_id}",
        json={"status": "resolved"},
        headers=auth(token),
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "resolved"


@pytest.mark.asyncio
async def test_support_tenant_isolation(async_client):
    token_a = await _register_and_token(async_client, email="usera@tenantahelp.com", org="TenantAHelp")
    token_b = await _register_and_token(async_client, email="userb@tenantbhelp.com", org="TenantBHelp")

    # Tenant A creates ticket
    resp = await async_client.post(
        f"{SUPPORT_BASE}/",
        json={
            "customer_email": "vip@important.com",
            "subject": "Confidential Security Inquiry",
            "description": "Details here...",
        },
        headers=auth(token_a),
    )
    assert resp.status_code == 201
    ticket_id = resp.json()["id"]

    # Tenant B attempts access -> 404
    resp_b = await async_client.get(f"{SUPPORT_BASE}/{ticket_id}", headers=auth(token_b))
    assert resp_b.status_code == 404

    # Tenant B list -> 0 tickets
    list_b = await async_client.get(f"{SUPPORT_BASE}/", headers=auth(token_b))
    assert list_b.status_code == 200
    assert len(list_b.json()) == 0
