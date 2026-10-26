"""Documents service — business logic."""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.models import Document, DocumentVersion, Folder
from app.documents.repository import DocumentRepository, DocumentVersionRepository, FolderRepository
from app.documents.schemas import DocumentCreate, DocumentUpdate, FolderCreate, FolderUpdate
from app.users.models import User


def _not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


class DocumentService:
    def __init__(self, session: AsyncSession, current_user: User) -> None:
        self.org_id: uuid.UUID = current_user.organization_id  # type: ignore[assignment]
        self.user_id: uuid.UUID = current_user.id
        self.folder_repo = FolderRepository(session)
        self.doc_repo = DocumentRepository(session)
        self.version_repo = DocumentVersionRepository(session)

    # ------------------------------------------------------------------
    # Folders
    # ------------------------------------------------------------------

    async def create_folder(self, data: FolderCreate) -> Folder:
        if data.parent_id:
            parent = await self.folder_repo.get(data.parent_id, self.org_id)
            if not parent:
                raise _not_found("Parent folder")
        return await self.folder_repo.create(self.org_id, self.user_id, data)

    async def get_folder(self, folder_id: uuid.UUID) -> Folder:
        folder = await self.folder_repo.get(folder_id, self.org_id)
        if not folder:
            raise _not_found("Folder")
        return folder

    async def list_folders(self, parent_id: Optional[uuid.UUID] = None) -> List[Folder]:
        return await self.folder_repo.list(self.org_id, parent_id=parent_id)

    async def update_folder(self, folder_id: uuid.UUID, data: FolderUpdate) -> Folder:
        folder = await self.get_folder(folder_id)
        if data.parent_id:
            if data.parent_id == folder_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A folder cannot be its own parent",
                )
            parent = await self.folder_repo.get(data.parent_id, self.org_id)
            if not parent:
                raise _not_found("Parent folder")
        return await self.folder_repo.update(folder, data)

    async def delete_folder(self, folder_id: uuid.UUID) -> None:
        folder = await self.get_folder(folder_id)
        await self.folder_repo.delete(folder)

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    async def create_document(self, data: DocumentCreate) -> Document:
        if data.folder_id:
            folder = await self.folder_repo.get(data.folder_id, self.org_id)
            if not folder:
                raise _not_found("Folder")
        return await self.doc_repo.create(self.org_id, self.user_id, data)

    async def get_document(self, doc_id: uuid.UUID) -> Document:
        doc = await self.doc_repo.get(doc_id, self.org_id)
        if not doc:
            raise _not_found("Document")
        return doc

    async def list_documents(
        self,
        folder_id: Optional[uuid.UUID] = None,
        include_archived: bool = False,
        search: Optional[str] = None,
    ) -> List[Document]:
        return await self.doc_repo.list(
            self.org_id,
            folder_id=folder_id,
            include_archived=include_archived,
            search=search,
        )

    async def update_document(self, doc_id: uuid.UUID, data: DocumentUpdate) -> Document:
        doc = await self.get_document(doc_id)
        if data.folder_id:
            folder = await self.folder_repo.get(data.folder_id, self.org_id)
            if not folder:
                raise _not_found("Folder")
        return await self.doc_repo.update(doc, data, self.user_id)

    async def delete_document(self, doc_id: uuid.UUID) -> None:
        doc = await self.get_document(doc_id)
        await self.doc_repo.delete(doc)

    # ------------------------------------------------------------------
    # Document Versions
    # ------------------------------------------------------------------

    async def list_versions(self, doc_id: uuid.UUID) -> List[DocumentVersion]:
        # Validate doc existence in org
        await self.get_document(doc_id)
        return await self.version_repo.list(doc_id, self.org_id)

    async def get_version(self, doc_id: uuid.UUID, version_id: uuid.UUID) -> DocumentVersion:
        await self.get_document(doc_id)
        version = await self.version_repo.get(version_id, self.org_id)
        if not version or version.document_id != doc_id:
            raise _not_found("Document version")
        return version
