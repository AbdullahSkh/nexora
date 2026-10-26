"""Integration tests for the Notifications module."""
import pytest

REGISTER_URL = "/api/v1/auth/register"
NOTIF_BASE = "/api/v1/notifications"


async def _register_and_info(client, email="notif@co.com", org="NotifOrg", password="Pass123!"):
    resp = await client.post(
        REGISTER_URL,
        json={
            "organization_name": org,
            "user_email": email,
            "password": password,
            "first_name": "Notif",
            "last_name": "User",
        },
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    # Get current user profile to obtain user id
    me_resp = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    user_id = me_resp.json()["id"]
    return token, user_id


def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_notifications_lifecycle(async_client):
    token, user_id = await _register_and_info(
        async_client, email="receiver@co.com", org="AlertsOrg"
    )

    # Initially 0 unread
    count_resp = await async_client.get(f"{NOTIF_BASE}/unread-count", headers=auth(token))
    assert count_resp.status_code == 200
    assert count_resp.json()["unread_count"] == 0

    # Send 2 notifications
    n1_resp = await async_client.post(
        f"{NOTIF_BASE}/",
        json={
            "recipient_id": user_id,
            "title": "New Task Assigned",
            "message": "You have been assigned to 'Fix Auth Bug'",
            "type": "task_assigned",
            "link": "/projects/tasks/123",
        },
        headers=auth(token),
    )
    assert n1_resp.status_code == 201
    n1_id = n1_resp.json()["id"]

    n2_resp = await async_client.post(
        f"{NOTIF_BASE}/",
        json={
            "recipient_id": user_id,
            "title": "Leave Approved",
            "message": "Your annual leave has been approved",
            "type": "leave_approved",
        },
        headers=auth(token),
    )
    assert n2_resp.status_code == 201

    # Check unread count is 2
    count_resp = await async_client.get(f"{NOTIF_BASE}/unread-count", headers=auth(token))
    assert count_resp.json()["unread_count"] == 2

    # Mark first notification as read
    read_resp = await async_client.post(f"{NOTIF_BASE}/{n1_id}/read", headers=auth(token))
    assert read_resp.status_code == 200
    assert read_resp.json()["is_read"] is True

    # Count is now 1
    count_resp = await async_client.get(f"{NOTIF_BASE}/unread-count", headers=auth(token))
    assert count_resp.json()["unread_count"] == 1

    # Mark all as read
    read_all_resp = await async_client.post(f"{NOTIF_BASE}/read-all", headers=auth(token))
    assert read_all_resp.status_code == 200

    # Count is now 0
    count_resp = await async_client.get(f"{NOTIF_BASE}/unread-count", headers=auth(token))
    assert count_resp.json()["unread_count"] == 0
