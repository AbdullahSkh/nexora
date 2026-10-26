"""Notifications repository — data access layer."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.models import Notification
from app.notifications.schemas import NotificationCreate


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, data: NotificationCreate) -> Notification:
        notif = Notification(
            **data.model_dump(),
            organization_id=org_id,
        )
        self.session.add(notif)
        await self.session.commit()
        await self.session.refresh(notif)
        return notif

    async def get(
        self, notif_id: uuid.UUID, user_id: uuid.UUID, org_id: uuid.UUID
    ) -> Optional[Notification]:
        result = await self.session.execute(
            select(Notification).where(
                Notification.id == notif_id,
                Notification.recipient_id == user_id,
                Notification.organization_id == org_id,
            )
        )
        return result.scalars().first()

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        org_id: uuid.UUID,
        unread_only: bool = False,
        limit: int = 50,
    ) -> List[Notification]:
        q = select(Notification).where(
            Notification.recipient_id == user_id,
            Notification.organization_id == org_id,
        )
        if unread_only:
            q = q.where(Notification.is_read == False)  # noqa: E712
        q = q.order_by(Notification.created_at.desc()).limit(limit)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def count_unread(self, user_id: uuid.UUID, org_id: uuid.UUID) -> int:
        result = await self.session.execute(
            select(func.count(Notification.id)).where(
                Notification.recipient_id == user_id,
                Notification.organization_id == org_id,
                Notification.is_read == False,  # noqa: E712
            )
        )
        return result.scalar() or 0

    async def mark_as_read(self, notification: Notification) -> Notification:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def mark_all_as_read(self, user_id: uuid.UUID, org_id: uuid.UUID) -> int:
        stmt = (
            update(Notification)
            .where(
                Notification.recipient_id == user_id,
                Notification.organization_id == org_id,
                Notification.is_read == False,  # noqa: E712
            )
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def delete(self, notification: Notification) -> None:
        await self.session.delete(notification)
        await self.session.commit()
