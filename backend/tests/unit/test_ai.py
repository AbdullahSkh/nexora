"""Integration tests for the AI module."""
import pytest

REGISTER_URL = "/api/v1/auth/register"
AI_BASE = "/api/v1/ai"


async def _register_and_token(client, email="aiuser@co.com", org="AIOrg", password="Pass123!"):
    resp = await client.post(
        REGISTER_URL,
        json={
            "organization_name": org,
            "user_email": email,
            "password": password,
            "first_name": "AI",
            "last_name": "User",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_ai_chat_and_tools(async_client):
    token = await _register_and_token(async_client, email="prompt@co.com", org="PromptCorp")

    # 1. Chat endpoint
    chat_resp = await async_client.post(
        f"{AI_BASE}/chat",
        json={
            "messages": [{"role": "user", "content": "How do I optimize our sales funnel?"}],
            "context_module": "crm",
        },
        headers=auth(token),
    )
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert "reply" in chat_data
    assert "model_used" in chat_data

    # 2. Summarize endpoint
    doc_text = """# Executive Meeting Minutes
- Finalized Q3 budget allocations for engineering team.
- Approved hiring of two backend senior developers.
- Discussed marketing roadmap for product launch in December."""
    sum_resp = await async_client.post(
        f"{AI_BASE}/summarize",
        json={"content": doc_text},
        headers=auth(token),
    )
    assert sum_resp.status_code == 200
    sum_data = sum_resp.json()
    assert "summary" in sum_data
    assert len(sum_data["key_points"]) > 0

    # 3. Generate copy endpoint
    copy_resp = await async_client.post(
        f"{AI_BASE}/generate-copy",
        json={
            "topic": "Feature Release v2.0",
            "copy_type": "email",
            "tone": "professional",
        },
        headers=auth(token),
    )
    assert copy_resp.status_code == 200
    copy_data = copy_resp.json()
    assert "Feature Release v2.0" in copy_data["generated_text"]
