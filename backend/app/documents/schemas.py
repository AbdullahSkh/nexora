"""Pydantic schemas for the Documents module."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Folder
# ---------------------------------------------------------------------------


class FolderBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None


class FolderCreate(FolderBase):
    pass


class FolderUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None


class FolderResponse(FolderBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Document Version
# ---------------------------------------------------------------------------


class DocumentVersionResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    document_id: uuid.UUID
    version_number: int
    title: str
    content: Optional[str] = None
    change_summary: Optional[str] = None
    created_by_id: Optional[uuid.UUID] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------


class DocumentBase(BaseModel):
    title: str
    content: Optional[str] = None
    folder_id: Optional[uuid.UUID] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    folder_id: Optional[uuid.UUID] = None
    is_archived: Optional[bool] = None
    change_summary: Optional[str] = None  # Notes what changed in this version


class DocumentResponse(DocumentBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    is_archived: bool
    created_by_id: Optional[uuid.UUID] = None
    updated_by_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DocumentDetailResponse(DocumentResponse):
    versions: List[DocumentVersionResponse] = []
    model_config = ConfigDict(from_attributes=True)
