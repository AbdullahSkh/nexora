"""Notifications API router."""
from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.notifications.schemas import (
    NotificationCreate,
    NotificationResponse,
    UnreadCountResponse,
)
from app.notifications.service import NotificationService
from app.users.models import User

router = APIRouter()


def _svc(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationService:
    return NotificationService(db, current_user)


@router.get("/", response_model=List[NotificationResponse])
async def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, le=100),
    svc: NotificationService = Depends(_svc),
):
    return await svc.list_notifications(unread_only=unread_only, limit=limit)


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(svc: NotificationService = Depends(_svc)):
    count = await svc.get_unread_count()
    return UnreadCountResponse(unread_count=count)


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def send_notification(
    data: NotificationCreate,
    svc: NotificationService = Depends(_svc),
):
    return await svc.send_notification(data)


@router.post("/{notif_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notif_id: uuid.UUID,
    svc: NotificationService = Depends(_svc),
):
    return await svc.mark_as_read(notif_id)


@router.post("/read-all", response_model=UnreadCountResponse)
async def mark_all_as_read(svc: NotificationService = Depends(_svc)):
    updated_count = await svc.mark_all_as_read()
    return UnreadCountResponse(unread_count=updated_count)


@router.delete("/{notif_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notif_id: uuid.UUID,
    svc: NotificationService = Depends(_svc),
):
    await svc.delete_notification(notif_id)
