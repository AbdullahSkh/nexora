"""Pydantic schemas for Support module."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.support.models import TicketPriority, TicketStatus


# ---------------------------------------------------------------------------
# Comment Schemas
# ---------------------------------------------------------------------------


class CommentCreate(BaseModel):
    body: str
    is_internal: bool = False


class CommentResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    ticket_id: uuid.UUID
    author_id: Optional[uuid.UUID] = None
    is_internal: bool
    body: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Ticket Schemas
# ---------------------------------------------------------------------------


class TicketBase(BaseModel):
    customer_email: EmailStr
    customer_name: Optional[str] = None
    subject: str
    description: str
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.MEDIUM
    assigned_to_id: Optional[uuid.UUID] = None


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    customer_email: Optional[EmailStr] = None
    customer_name: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to_id: Optional[uuid.UUID] = None


class TicketResponse(TicketBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TicketDetailResponse(TicketResponse):
    comments: List[CommentResponse] = []
    model_config = ConfigDict(from_attributes=True)
