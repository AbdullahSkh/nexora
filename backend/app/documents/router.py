"""Documents API router."""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.documents.schemas import (
    DocumentCreate,
    DocumentDetailResponse,
    DocumentResponse,
    DocumentUpdate,
    DocumentVersionResponse,
    FolderCreate,
    FolderResponse,
    FolderUpdate,
)
from app.documents.service import DocumentService
from app.users.models import User

router = APIRouter()


def _svc(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentService:
    return DocumentService(db, current_user)


# ---------------------------------------------------------------------------
# Folders
# ---------------------------------------------------------------------------


@router.post("/folders", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(data: FolderCreate, svc: DocumentService = Depends(_svc)):
    return await svc.create_folder(data)


@router.get("/folders", response_model=List[FolderResponse])
async def list_folders(
    parent_id: Optional[uuid.UUID] = Query(None),
    svc: DocumentService = Depends(_svc),
):
    return await svc.list_folders(parent_id=parent_id)


@router.get("/folders/{folder_id}", response_model=FolderResponse)
async def get_folder(folder_id: uuid.UUID, svc: DocumentService = Depends(_svc)):
    return await svc.get_folder(folder_id)


@router.patch("/folders/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: uuid.UUID,
    data: FolderUpdate,
    svc: DocumentService = Depends(_svc),
):
    return await svc.update_folder(folder_id, data)


@router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(folder_id: uuid.UUID, svc: DocumentService = Depends(_svc)):
    await svc.delete_folder(folder_id)


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(data: DocumentCreate, svc: DocumentService = Depends(_svc)):
    return await svc.create_document(data)


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    folder_id: Optional[uuid.UUID] = Query(None),
    include_archived: bool = Query(False),
    search: Optional[str] = Query(None),
    svc: DocumentService = Depends(_svc),
):
    return await svc.list_documents(
        folder_id=folder_id,
        include_archived=include_archived,
        search=search,
    )


@router.get("/{doc_id}", response_model=DocumentDetailResponse)
async def get_document(doc_id: uuid.UUID, svc: DocumentService = Depends(_svc)):
    return await svc.get_document(doc_id)


@router.patch("/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: uuid.UUID,
    data: DocumentUpdate,
    svc: DocumentService = Depends(_svc),
):
    return await svc.update_document(doc_id, data)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(doc_id: uuid.UUID, svc: DocumentService = Depends(_svc)):
    await svc.delete_document(doc_id)


# ---------------------------------------------------------------------------
# Document Versions
# ---------------------------------------------------------------------------


@router.get("/{doc_id}/versions", response_model=List[DocumentVersionResponse])
async def list_document_versions(doc_id: uuid.UUID, svc: DocumentService = Depends(_svc)):
    return await svc.list_versions(doc_id)


@router.get("/{doc_id}/versions/{version_id}", response_model=DocumentVersionResponse)
async def get_document_version(
    doc_id: uuid.UUID,
    version_id: uuid.UUID,
    svc: DocumentService = Depends(_svc),
):
    return await svc.get_version(doc_id, version_id)
