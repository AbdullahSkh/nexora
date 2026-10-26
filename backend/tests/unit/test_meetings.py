"""Integration tests for the Meetings module.

Covers Meetings, Notes, Action Items, Attendees, and Multi-tenancy isolation.
"""
from datetime import datetime, timezone, timedelta
import pytest

REGISTER_URL = "/api/v1/auth/register"
MEETINGS_BASE = "/api/v1/meetings"


async def _register_and_token(client, email="meet@co.com", org="MeetOrg", password="Pass123!"):
    resp = await client.post(
        REGISTER_URL,
        json={
            "organization_name": org,
            "user_email": email,
            "password": password,
            "first_name": "Meet",
            "last_name": "Organizer",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_and_detail_meeting(async_client):
    token = await _register_and_token(async_client, email="organizer1@co.com", org="OrgMeet1")

    now = datetime.now(timezone.utc)
    start_time = (now + timedelta(days=1)).isoformat()
    end_time = (now + timedelta(days=1, hours=1)).isoformat()

    meeting_payload = {
        "title": "Weekly Sprint Planning",
        "description": "Discuss sprint backlog and assignments",
        "start_time": start_time,
        "end_time": end_time,
        "location": "https://meet.google.com/abc-defg-hij",
        "attendees": [
            {"email": "dev1@co.com", "status": "invited"},
            {"email": "dev2@co.com", "status": "invited"},
        ],
    }

    create_resp = await async_client.post(
        f"{MEETINGS_BASE}/",
        json=meeting_payload,
        headers=auth(token),
    )
    assert create_resp.status_code == 201
    meeting = create_resp.json()
    assert meeting["title"] == "Weekly Sprint Planning"
    meeting_id = meeting["id"]

    # Fetch meeting detail
    detail_resp = await async_client.get(f"{MEETINGS_BASE}/{meeting_id}", headers=auth(token))
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert len(detail["attendees"]) == 2
    assert detail["attendees"][0]["email"] in ["dev1@co.com", "dev2@co.com"]

    # Add Note
    note_resp = await async_client.post(
        f"{MEETINGS_BASE}/{meeting_id}/notes",
        json={"content": "Agreed on delivering billing portal first."},
        headers=auth(token),
    )
    assert note_resp.status_code == 201
    assert note_resp.json()["content"] == "Agreed on delivering billing portal first."

    # Add Action Item
    item_resp = await async_client.post(
        f"{MEETINGS_BASE}/{meeting_id}/action-items",
        json={"title": "Draft API spec for billing", "due_date": "2026-11-01"},
        headers=auth(token),
    )
    assert item_resp.status_code == 201
    item_id = item_resp.json()["id"]
    assert item_resp.json()["is_completed"] is False

    # Mark action item as completed
    update_item = await async_client.patch(
        f"{MEETINGS_BASE}/action-items/{item_id}",
        json={"is_completed": True},
        headers=auth(token),
    )
    assert update_item.status_code == 200
    assert update_item.json()["is_completed"] is True


@pytest.mark.asyncio
async def test_meeting_tenant_isolation(async_client):
    token_a = await _register_and_token(async_client, email="usera@tenanta.com", org="TenantAMeet")
    token_b = await _register_and_token(async_client, email="userb@tenantb.com", org="TenantBMeet")

    now = datetime.now(timezone.utc)
    meeting_payload = {
        "title": "Secret Strategy Meeting",
        "start_time": (now + timedelta(hours=2)).isoformat(),
        "end_time": (now + timedelta(hours=3)).isoformat(),
    }

    create_resp = await async_client.post(
        f"{MEETINGS_BASE}/",
        json=meeting_payload,
        headers=auth(token_a),
    )
    assert create_resp.status_code == 201
    meeting_id = create_resp.json()["id"]

    # Tenant B tries to get Tenant A's meeting -> 404
    resp = await async_client.get(f"{MEETINGS_BASE}/{meeting_id}", headers=auth(token_b))
    assert resp.status_code == 404

    # Tenant B tries to add a note -> 404
    resp = await async_client.post(
        f"{MEETINGS_BASE}/{meeting_id}/notes",
        json={"content": "Hacker note"},
        headers=auth(token_b),
    )
    assert resp.status_code == 404

    # Tenant B listing has 0 items
    list_resp = await async_client.get(f"{MEETINGS_BASE}/", headers=auth(token_b))
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 0
