"""Meetings service — business logic."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.meetings.models import Meeting, MeetingActionItem, MeetingAttendee, MeetingNote
from app.meetings.repository import (
    MeetingActionItemRepository,
    MeetingAttendeeRepository,
    MeetingNoteRepository,
    MeetingRepository,
)
from app.meetings.schemas import (
    ActionItemCreate,
    ActionItemUpdate,
    AttendeeCreate,
    AttendeeUpdate,
    MeetingCreate,
    MeetingUpdate,
    NoteCreate,
)
from app.users.models import User


def _not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


class MeetingService:
    def __init__(self, session: AsyncSession, current_user: User) -> None:
        self.org_id: uuid.UUID = current_user.organization_id  # type: ignore[assignment]
        self.user_id: uuid.UUID = current_user.id
        self.meeting_repo = MeetingRepository(session)
        self.note_repo = MeetingNoteRepository(session)
        self.action_item_repo = MeetingActionItemRepository(session)
        self.attendee_repo = MeetingAttendeeRepository(session)

    # ------------------------------------------------------------------
    # Meetings
    # ------------------------------------------------------------------

    async def create_meeting(self, data: MeetingCreate) -> Meeting:
        return await self.meeting_repo.create(self.org_id, self.user_id, data)

    async def get_meeting(self, meeting_id: uuid.UUID) -> Meeting:
        meeting = await self.meeting_repo.get(meeting_id, self.org_id)
        if not meeting:
            raise _not_found("Meeting")
        return meeting

    async def list_meetings(
        self,
        status: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> List[Meeting]:
        return await self.meeting_repo.list(
            self.org_id,
            status=status,
            from_date=from_date,
            to_date=to_date,
        )

    async def update_meeting(self, meeting_id: uuid.UUID, data: MeetingUpdate) -> Meeting:
        meeting = await self.get_meeting(meeting_id)
        return await self.meeting_repo.update(meeting, data)

    async def delete_meeting(self, meeting_id: uuid.UUID) -> None:
        meeting = await self.get_meeting(meeting_id)
        await self.meeting_repo.delete(meeting)

    # ------------------------------------------------------------------
    # Meeting Notes
    # ------------------------------------------------------------------

    async def add_note(self, meeting_id: uuid.UUID, data: NoteCreate) -> MeetingNote:
        await self.get_meeting(meeting_id)
        return await self.note_repo.create(self.org_id, meeting_id, self.user_id, data)

    async def list_notes(self, meeting_id: uuid.UUID) -> List[MeetingNote]:
        await self.get_meeting(meeting_id)
        return await self.note_repo.list(meeting_id, self.org_id)

    # ------------------------------------------------------------------
    # Action Items
    # ------------------------------------------------------------------

    async def add_action_item(
        self, meeting_id: uuid.UUID, data: ActionItemCreate
    ) -> MeetingActionItem:
        await self.get_meeting(meeting_id)
        return await self.action_item_repo.create(self.org_id, meeting_id, data)

    async def list_action_items(self, meeting_id: uuid.UUID) -> List[MeetingActionItem]:
        await self.get_meeting(meeting_id)
        return await self.action_item_repo.list(meeting_id, self.org_id)

    async def update_action_item(
        self, item_id: uuid.UUID, data: ActionItemUpdate
    ) -> MeetingActionItem:
        item = await self.action_item_repo.get(item_id, self.org_id)
        if not item:
            raise _not_found("Action item")
        return await self.action_item_repo.update(item, data)

    async def delete_action_item(self, item_id: uuid.UUID) -> None:
        item = await self.action_item_repo.get(item_id, self.org_id)
        if not item:
            raise _not_found("Action item")
        await self.action_item_repo.delete(item)

    # ------------------------------------------------------------------
    # Attendees
    # ------------------------------------------------------------------

    async def add_attendee(self, meeting_id: uuid.UUID, data: AttendeeCreate) -> MeetingAttendee:
        await self.get_meeting(meeting_id)
        return await self.attendee_repo.create(self.org_id, meeting_id, data)

    async def update_attendee(
        self, attendee_id: uuid.UUID, data: AttendeeUpdate
    ) -> MeetingAttendee:
        attendee = await self.attendee_repo.get(attendee_id, self.org_id)
        if not attendee:
            raise _not_found("Attendee")
        return await self.attendee_repo.update(attendee, data)

    async def delete_attendee(self, attendee_id: uuid.UUID) -> None:
        attendee = await self.attendee_repo.get(attendee_id, self.org_id)
        if not attendee:
            raise _not_found("Attendee")
        await self.attendee_repo.delete(attendee)
