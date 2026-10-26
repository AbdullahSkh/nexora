"""Documents repository — data access layer."""
from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.models import Document, DocumentVersion, Folder
from app.documents.schemas import FolderCreate, FolderUpdate, DocumentCreate, DocumentUpdate


class FolderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, user_id: uuid.UUID, data: FolderCreate) -> Folder:
        obj = Folder(
            **data.model_dump(),
            organization_id=org_id,
            created_by_id=user_id,
        )
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, folder_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Folder]:
        result = await self.session.execute(
            select(Folder).where(Folder.id == folder_id, Folder.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(self, org_id: uuid.UUID, parent_id: Optional[uuid.UUID] = None) -> List[Folder]:
        q = select(Folder).where(Folder.organization_id == org_id)
        if parent_id is not None:
            q = q.where(Folder.parent_id == parent_id)
        result = await self.session.execute(q.order_by(Folder.name.asc()))
        return list(result.scalars().all())

    async def update(self, folder: Folder, data: FolderUpdate) -> Folder:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(folder, field, value)
        self.session.add(folder)
        await self.session.commit()
        await self.session.refresh(folder)
        return folder

    async def delete(self, folder: Folder) -> None:
        await self.session.delete(folder)
        await self.session.commit()


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, user_id: uuid.UUID, data: DocumentCreate) -> Document:
        doc = Document(
            **data.model_dump(),
            organization_id=org_id,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        self.session.add(doc)
        await self.session.flush()

        # Create initial Version 1
        initial_version = DocumentVersion(
            organization_id=org_id,
            document_id=doc.id,
            version_number=1,
            title=doc.title,
            content=doc.content,
            change_summary="Initial document creation",
            created_by_id=user_id,
        )
        self.session.add(initial_version)
        await self.session.commit()
        await self.session.refresh(doc)
        return doc

    async def get(self, doc_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Document]:
        result = await self.session.execute(
            select(Document)
            .options(selectinload(Document.versions))
            .where(Document.id == doc_id, Document.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(
        self,
        org_id: uuid.UUID,
        folder_id: Optional[uuid.UUID] = None,
        include_archived: bool = False,
        search: Optional[str] = None,
    ) -> List[Document]:
        q = select(Document).where(Document.organization_id == org_id)
        if not include_archived:
            q = q.where(Document.is_archived == False)  # noqa: E712
        if folder_id is not None:
            q = q.where(Document.folder_id == folder_id)
        if search:
            search_pattern = f"%{search}%"
            q = q.where(
                or_(
                    Document.title.ilike(search_pattern),
                    Document.content.ilike(search_pattern),
                )
            )
        result = await self.session.execute(q.order_by(Document.updated_at.desc()))
        return list(result.scalars().all())

    async def update(self, doc: Document, data: DocumentUpdate, user_id: uuid.UUID) -> Document:
        title_changed = data.title is not None and data.title != doc.title
        content_changed = data.content is not None and data.content != doc.content

        update_dict = data.model_dump(exclude_unset=True)
        change_summary = update_dict.pop("change_summary", None)

        for field, value in update_dict.items():
            setattr(doc, field, value)
        doc.updated_by_id = user_id
        self.session.add(doc)

        # If title or content changed, record a new version
        if title_changed or content_changed:
            await self.session.flush()
            # Find current max version number
            version_result = await self.session.execute(
                select(DocumentVersion.version_number)
                .where(DocumentVersion.document_id == doc.id)
                .order_by(DocumentVersion.version_number.desc())
                .limit(1)
            )
            latest_version_num = version_result.scalar() or 1
            new_version = DocumentVersion(
                organization_id=doc.organization_id,
                document_id=doc.id,
                version_number=latest_version_num + 1,
                title=doc.title,
                content=doc.content,
                change_summary=change_summary or f"Updated to version {latest_version_num + 1}",
                created_by_id=user_id,
            )
            self.session.add(new_version)

        await self.session.commit()
        await self.session.refresh(doc)
        return doc

    async def delete(self, doc: Document) -> None:
        await self.session.delete(doc)
        await self.session.commit()


class DocumentVersionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self, document_id: uuid.UUID, org_id: uuid.UUID) -> List[DocumentVersion]:
        result = await self.session.execute(
            select(DocumentVersion)
            .where(
                DocumentVersion.document_id == document_id,
                DocumentVersion.organization_id == org_id,
            )
            .order_by(DocumentVersion.version_number.desc())
        )
        return list(result.scalars().all())

    async def get(self, version_id: uuid.UUID, org_id: uuid.UUID) -> Optional[DocumentVersion]:
        result = await self.session.execute(
            select(DocumentVersion).where(
                DocumentVersion.id == version_id,
                DocumentVersion.organization_id == org_id,
            )
        )
        return result.scalars().first()
