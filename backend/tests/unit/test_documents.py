"""Integration tests for the Documents module.

Covers Folders, Documents, Versioning, and Multi-tenancy isolation.
"""
import pytest

REGISTER_URL = "/api/v1/auth/register"
DOCS_BASE = "/api/v1/documents"


async def _register_and_token(client, email="admin@co.com", org="DocOrg", password="Pass123!"):
    resp = await client.post(
        REGISTER_URL,
        json={
            "organization_name": org,
            "user_email": email,
            "password": password,
            "first_name": "Doc",
            "last_name": "Admin",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_and_list_folders(async_client):
    token = await _register_and_token(async_client, email="folder_test@co.com", org="FolderOrg")

    resp = await async_client.post(
        f"{DOCS_BASE}/folders",
        json={"name": "Engineering", "description": "All tech specs"},
        headers=auth(token),
    )
    assert resp.status_code == 201
    folder_data = resp.json()
    assert folder_data["name"] == "Engineering"
    folder_id = folder_data["id"]

    # Create subfolder
    sub_resp = await async_client.post(
        f"{DOCS_BASE}/folders",
        json={"name": "Architecture", "parent_id": folder_id},
        headers=auth(token),
    )
    assert sub_resp.status_code == 201
    assert sub_resp.json()["parent_id"] == folder_id

    # List folders
    list_resp = await async_client.get(f"{DOCS_BASE}/folders", headers=auth(token))
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 2


@pytest.mark.asyncio
async def test_create_document_and_versions(async_client):
    token = await _register_and_token(async_client, email="doc_test@co.com", org="DocsOrg")

    # Create document
    create_resp = await async_client.post(
        f"{DOCS_BASE}/",
        json={"title": "Product Roadmap", "content": "# Roadmap v1\nInitial draft"},
        headers=auth(token),
    )
    assert create_resp.status_code == 201
    doc = create_resp.json()
    doc_id = doc["id"]
    assert doc["title"] == "Product Roadmap"

    # Fetch document detail (should have 1 version automatically created)
    detail_resp = await async_client.get(f"{DOCS_BASE}/{doc_id}", headers=auth(token))
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert len(detail["versions"]) == 1
    assert detail["versions"][0]["version_number"] == 1

    # Update document content
    update_resp = await async_client.patch(
        f"{DOCS_BASE}/{doc_id}",
        json={"content": "# Roadmap v2\nUpdated features", "change_summary": "Added Q2 goals"},
        headers=auth(token),
    )
    assert update_resp.status_code == 200

    # Fetch versions
    versions_resp = await async_client.get(f"{DOCS_BASE}/{doc_id}/versions", headers=auth(token))
    assert versions_resp.status_code == 200
    versions = versions_resp.json()
    assert len(versions) == 2
    assert versions[0]["version_number"] == 2
    assert versions[0]["change_summary"] == "Added Q2 goals"


@pytest.mark.asyncio
async def test_document_search_and_archive(async_client):
    token = await _register_and_token(async_client, email="search_test@co.com", org="SearchOrg")

    await async_client.post(
        f"{DOCS_BASE}/",
        json={"title": "Backend Architecture", "content": "FastAPI and Postgres"},
        headers=auth(token),
    )
    await async_client.post(
        f"{DOCS_BASE}/",
        json={"title": "Frontend Guidelines", "content": "React and Tailwind/CSS"},
        headers=auth(token),
    )

    # Search for Postgres
    resp = await async_client.get(f"{DOCS_BASE}/?search=Postgres", headers=auth(token))
    assert resp.status_code == 200
    docs = resp.json()
    assert len(docs) == 1
    assert docs[0]["title"] == "Backend Architecture"


@pytest.mark.asyncio
async def test_documents_tenant_isolation(async_client):
    token_a = await _register_and_token(async_client, email="a@tenanta.com", org="TenantA")
    token_b = await _register_and_token(async_client, email="b@tenantb.com", org="TenantB")

    # Tenant A creates folder and document
    folder_resp = await async_client.post(
        f"{DOCS_BASE}/folders",
        json={"name": "A Secret Folder"},
        headers=auth(token_a),
    )
    folder_id = folder_resp.json()["id"]

    doc_resp = await async_client.post(
        f"{DOCS_BASE}/",
        json={"title": "A Confidential Doc", "folder_id": folder_id},
        headers=auth(token_a),
    )
    doc_id = doc_resp.json()["id"]

    # Tenant B tries to get folder -> 404
    resp = await async_client.get(f"{DOCS_BASE}/folders/{folder_id}", headers=auth(token_b))
    assert resp.status_code == 404

    # Tenant B tries to get doc -> 404
    resp = await async_client.get(f"{DOCS_BASE}/{doc_id}", headers=auth(token_b))
    assert resp.status_code == 404

    # Tenant B listing should be empty
    resp = await async_client.get(f"{DOCS_BASE}/", headers=auth(token_b))
    assert resp.status_code == 200
    assert len(resp.json()) == 0
