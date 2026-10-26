"""Pydantic schemas for Notifications module."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificationCreate(BaseModel):
    recipient_id: uuid.UUID
    title: str
    message: str
    type: str = "system"
    link: Optional[str] = None


class NotificationResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    recipient_id: uuid.UUID
    title: str
    message: str
    type: str
    link: Optional[str] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UnreadCountResponse(BaseModel):
    unread_count: int
