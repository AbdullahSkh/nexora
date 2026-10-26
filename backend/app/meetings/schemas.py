"""Pydantic schemas for Meetings module."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.meetings.models import AttendeeStatus, MeetingStatus


# ---------------------------------------------------------------------------
# Attendee Schemas
# ---------------------------------------------------------------------------


class AttendeeCreate(BaseModel):
    email: str
    user_id: Optional[uuid.UUID] = None
    status: AttendeeStatus = AttendeeStatus.INVITED


class AttendeeUpdate(BaseModel):
    status: AttendeeStatus


class AttendeeResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    meeting_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    email: str
    status: AttendeeStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Note Schemas
# ---------------------------------------------------------------------------


class NoteCreate(BaseModel):
    content: str


class NoteResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    meeting_id: uuid.UUID
    created_by_id: Optional[uuid.UUID] = None
    content: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Action Item Schemas
# ---------------------------------------------------------------------------


class ActionItemCreate(BaseModel):
    title: str
    assignee_id: Optional[uuid.UUID] = None
    due_date: Optional[str] = None


class ActionItemUpdate(BaseModel):
    title: Optional[str] = None
    assignee_id: Optional[uuid.UUID] = None
    due_date: Optional[str] = None
    is_completed: Optional[bool] = None


class ActionItemResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    meeting_id: uuid.UUID
    assignee_id: Optional[uuid.UUID] = None
    title: str
    due_date: Optional[str] = None
    is_completed: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Meeting Schemas
# ---------------------------------------------------------------------------


class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    status: MeetingStatus = MeetingStatus.SCHEDULED


class MeetingCreate(MeetingBase):
    attendees: Optional[List[AttendeeCreate]] = None


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    status: Optional[MeetingStatus] = None


class MeetingResponse(MeetingBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    organizer_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MeetingDetailResponse(MeetingResponse):
    attendees: List[AttendeeResponse] = []
    notes: List[NoteResponse] = []
    action_items: List[ActionItemResponse] = []
    model_config = ConfigDict(from_attributes=True)
