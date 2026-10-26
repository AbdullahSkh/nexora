"""Meetings API router."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.meetings.schemas import (
    ActionItemCreate,
    ActionItemResponse,
    ActionItemUpdate,
    AttendeeCreate,
    AttendeeResponse,
    AttendeeUpdate,
    MeetingCreate,
    MeetingDetailResponse,
    MeetingResponse,
    MeetingUpdate,
    NoteCreate,
    NoteResponse,
)
from app.meetings.service import MeetingService
from app.users.models import User

router = APIRouter()


def _svc(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MeetingService:
    return MeetingService(db, current_user)


# ---------------------------------------------------------------------------
# Meetings
# ---------------------------------------------------------------------------


@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(data: MeetingCreate, svc: MeetingService = Depends(_svc)):
    return await svc.create_meeting(data)


@router.get("/", response_model=List[MeetingResponse])
async def list_meetings(
    meeting_status: Optional[str] = Query(None, alias="status"),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    svc: MeetingService = Depends(_svc),
):
    return await svc.list_meetings(
        status=meeting_status,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/{meeting_id}", response_model=MeetingDetailResponse)
async def get_meeting(meeting_id: uuid.UUID, svc: MeetingService = Depends(_svc)):
    return await svc.get_meeting(meeting_id)


@router.patch("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: uuid.UUID,
    data: MeetingUpdate,
    svc: MeetingService = Depends(_svc),
):
    return await svc.update_meeting(meeting_id, data)


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(meeting_id: uuid.UUID, svc: MeetingService = Depends(_svc)):
    await svc.delete_meeting(meeting_id)


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------


@router.post("/{meeting_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def add_note(
    meeting_id: uuid.UUID,
    data: NoteCreate,
    svc: MeetingService = Depends(_svc),
):
    return await svc.add_note(meeting_id, data)


@router.get("/{meeting_id}/notes", response_model=List[NoteResponse])
async def list_notes(meeting_id: uuid.UUID, svc: MeetingService = Depends(_svc)):
    return await svc.list_notes(meeting_id)


# ---------------------------------------------------------------------------
# Action Items
# ---------------------------------------------------------------------------


@router.post(
    "/{meeting_id}/action-items",
    response_model=ActionItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_action_item(
    meeting_id: uuid.UUID,
    data: ActionItemCreate,
    svc: MeetingService = Depends(_svc),
):
    return await svc.add_action_item(meeting_id, data)


@router.get("/{meeting_id}/action-items", response_model=List[ActionItemResponse])
async def list_action_items(meeting_id: uuid.UUID, svc: MeetingService = Depends(_svc)):
    return await svc.list_action_items(meeting_id)


@router.patch("/action-items/{item_id}", response_model=ActionItemResponse)
async def update_action_item(
    item_id: uuid.UUID,
    data: ActionItemUpdate,
    svc: MeetingService = Depends(_svc),
):
    return await svc.update_action_item(item_id, data)


@router.delete("/action-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action_item(item_id: uuid.UUID, svc: MeetingService = Depends(_svc)):
    await svc.delete_action_item(item_id)


# ---------------------------------------------------------------------------
# Attendees
# ---------------------------------------------------------------------------


@router.post(
    "/{meeting_id}/attendees",
    response_model=AttendeeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_attendee(
    meeting_id: uuid.UUID,
    data: AttendeeCreate,
    svc: MeetingService = Depends(_svc),
):
    return await svc.add_attendee(meeting_id, data)


@router.patch("/attendees/{attendee_id}", response_model=AttendeeResponse)
async def update_attendee(
    attendee_id: uuid.UUID,
    data: AttendeeUpdate,
    svc: MeetingService = Depends(_svc),
):
    return await svc.update_attendee(attendee_id, data)


@router.delete("/attendees/{attendee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendee(attendee_id: uuid.UUID, svc: MeetingService = Depends(_svc)):
    await svc.delete_attendee(attendee_id)
