"""Meetings repository — data access layer."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.meetings.models import Meeting, MeetingActionItem, MeetingAttendee, MeetingNote
from app.meetings.schemas import (
    ActionItemCreate,
    ActionItemUpdate,
    AttendeeCreate,
    AttendeeUpdate,
    MeetingCreate,
    MeetingUpdate,
    NoteCreate,
)


class MeetingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, user_id: uuid.UUID, data: MeetingCreate) -> Meeting:
        meeting_dict = data.model_dump(exclude={"attendees"})
        meeting = Meeting(
            **meeting_dict,
            organization_id=org_id,
            organizer_id=user_id,
        )
        self.session.add(meeting)
        await self.session.flush()

        if data.attendees:
            for att_data in data.attendees:
                attendee = MeetingAttendee(
                    **att_data.model_dump(),
                    organization_id=org_id,
                    meeting_id=meeting.id,
                )
                self.session.add(attendee)

        await self.session.commit()
        await self.session.refresh(meeting)
        return meeting

    async def get(self, meeting_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Meeting]:
        result = await self.session.execute(
            select(Meeting)
            .options(
                selectinload(Meeting.attendees),
                selectinload(Meeting.notes),
                selectinload(Meeting.action_items),
            )
            .where(Meeting.id == meeting_id, Meeting.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(
        self,
        org_id: uuid.UUID,
        status: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> List[Meeting]:
        q = select(Meeting).where(Meeting.organization_id == org_id)
        if status:
            q = q.where(Meeting.status == status)
        if from_date:
            q = q.where(Meeting.start_time >= from_date)
        if to_date:
            q = q.where(Meeting.end_time <= to_date)
        result = await self.session.execute(q.order_by(Meeting.start_time.asc()))
        return list(result.scalars().all())

    async def update(self, meeting: Meeting, data: MeetingUpdate) -> Meeting:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(meeting, field, value)
        self.session.add(meeting)
        await self.session.commit()
        await self.session.refresh(meeting)
        return meeting

    async def delete(self, meeting: Meeting) -> None:
        await self.session.delete(meeting)
        await self.session.commit()


class MeetingNoteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        org_id: uuid.UUID,
        meeting_id: uuid.UUID,
        user_id: uuid.UUID,
        data: NoteCreate,
    ) -> MeetingNote:
        note = MeetingNote(
            **data.model_dump(),
            organization_id=org_id,
            meeting_id=meeting_id,
            created_by_id=user_id,
        )
        self.session.add(note)
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def list(self, meeting_id: uuid.UUID, org_id: uuid.UUID) -> List[MeetingNote]:
        result = await self.session.execute(
            select(MeetingNote)
            .where(
                MeetingNote.meeting_id == meeting_id,
                MeetingNote.organization_id == org_id,
            )
            .order_by(MeetingNote.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, note: MeetingNote) -> None:
        await self.session.delete(note)
        await self.session.commit()


class MeetingActionItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        org_id: uuid.UUID,
        meeting_id: uuid.UUID,
        data: ActionItemCreate,
    ) -> MeetingActionItem:
        item = MeetingActionItem(
            **data.model_dump(),
            organization_id=org_id,
            meeting_id=meeting_id,
        )
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def get(self, item_id: uuid.UUID, org_id: uuid.UUID) -> Optional[MeetingActionItem]:
        result = await self.session.execute(
            select(MeetingActionItem).where(
                MeetingActionItem.id == item_id,
                MeetingActionItem.organization_id == org_id,
            )
        )
        return result.scalars().first()

    async def list(self, meeting_id: uuid.UUID, org_id: uuid.UUID) -> List[MeetingActionItem]:
        result = await self.session.execute(
            select(MeetingActionItem)
            .where(
                MeetingActionItem.meeting_id == meeting_id,
                MeetingActionItem.organization_id == org_id,
            )
            .order_by(MeetingActionItem.created_at.asc())
        )
        return list(result.scalars().all())

    async def update(self, item: MeetingActionItem, data: ActionItemUpdate) -> MeetingActionItem:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def delete(self, item: MeetingActionItem) -> None:
        await self.session.delete(item)
        await self.session.commit()


class MeetingAttendeeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        org_id: uuid.UUID,
        meeting_id: uuid.UUID,
        data: AttendeeCreate,
    ) -> MeetingAttendee:
        attendee = MeetingAttendee(
            **data.model_dump(),
            organization_id=org_id,
            meeting_id=meeting_id,
        )
        self.session.add(attendee)
        await self.session.commit()
        await self.session.refresh(attendee)
        return attendee

    async def get(self, attendee_id: uuid.UUID, org_id: uuid.UUID) -> Optional[MeetingAttendee]:
        result = await self.session.execute(
            select(MeetingAttendee).where(
                MeetingAttendee.id == attendee_id,
                MeetingAttendee.organization_id == org_id,
            )
        )
        return result.scalars().first()

    async def update(self, attendee: MeetingAttendee, data: AttendeeUpdate) -> MeetingAttendee:
        attendee.status = data.status
        self.session.add(attendee)
        await self.session.commit()
        await self.session.refresh(attendee)
        return attendee

    async def delete(self, attendee: MeetingAttendee) -> None:
        await self.session.delete(attendee)
        await self.session.commit()
