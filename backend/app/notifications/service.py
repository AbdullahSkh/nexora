"""Notifications service — business logic."""
from __future__ import annotations

import uuid
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.models import Notification
from app.notifications.repository import NotificationRepository
from app.notifications.schemas import NotificationCreate
from app.users.models import User


def _not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


class NotificationService:
    def __init__(self, session: AsyncSession, current_user: User) -> None:
        self.org_id: uuid.UUID = current_user.organization_id  # type: ignore[assignment]
        self.user_id: uuid.UUID = current_user.id
        self.repo = NotificationRepository(session)

    async def send_notification(self, data: NotificationCreate) -> Notification:
        return await self.repo.create(self.org_id, data)

    async def list_notifications(
        self, unread_only: bool = False, limit: int = 50
    ) -> List[Notification]:
        return await self.repo.list_for_user(
            self.user_id, self.org_id, unread_only=unread_only, limit=limit
        )

    async def get_unread_count(self) -> int:
        return await self.repo.count_unread(self.user_id, self.org_id)

    async def mark_as_read(self, notif_id: uuid.UUID) -> Notification:
        notif = await self.repo.get(notif_id, self.user_id, self.org_id)
        if not notif:
            raise _not_found("Notification")
        return await self.repo.mark_as_read(notif)

    async def mark_all_as_read(self) -> int:
        return await self.repo.mark_all_as_read(self.user_id, self.org_id)

    async def delete_notification(self, notif_id: uuid.UUID) -> None:
        notif = await self.repo.get(notif_id, self.user_id, self.org_id)
        if not notif:
            raise _not_found("Notification")
        await self.repo.delete(notif)
