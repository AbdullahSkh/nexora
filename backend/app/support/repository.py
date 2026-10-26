"""Support repository — data access layer."""
from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.support.models import Ticket, TicketComment
from app.support.schemas import CommentCreate, TicketCreate, TicketUpdate


class TicketRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, user_id: Optional[uuid.UUID], data: TicketCreate) -> Ticket:
        ticket = Ticket(
            **data.model_dump(),
            organization_id=org_id,
            created_by_id=user_id,
        )
        self.session.add(ticket)
        await self.session.commit()
        await self.session.refresh(ticket)
        return ticket

    async def get(self, ticket_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Ticket]:
        result = await self.session.execute(
            select(Ticket)
            .options(selectinload(Ticket.comments))
            .where(Ticket.id == ticket_id, Ticket.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(
        self,
        org_id: uuid.UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
    ) -> List[Ticket]:
        q = select(Ticket).where(Ticket.organization_id == org_id)
        if status:
            q = q.where(Ticket.status == status)
        if priority:
            q = q.where(Ticket.priority == priority)
        if assigned_to_id:
            q = q.where(Ticket.assigned_to_id == assigned_to_id)
        if search:
            search_pat = f"%{search}%"
            q = q.where(
                or_(
                    Ticket.subject.ilike(search_pat),
                    Ticket.customer_email.ilike(search_pat),
                    Ticket.customer_name.ilike(search_pat),
                )
            )
        result = await self.session.execute(q.order_by(Ticket.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, ticket: Ticket, data: TicketUpdate) -> Ticket:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(ticket, field, value)
        self.session.add(ticket)
        await self.session.commit()
        await self.session.refresh(ticket)
        return ticket

    async def delete(self, ticket: Ticket) -> None:
        await self.session.delete(ticket)
        await self.session.commit()


class TicketCommentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        org_id: uuid.UUID,
        ticket_id: uuid.UUID,
        author_id: Optional[uuid.UUID],
        data: CommentCreate,
    ) -> TicketComment:
        comment = TicketComment(
            **data.model_dump(),
            organization_id=org_id,
            ticket_id=ticket_id,
            author_id=author_id,
        )
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def list(self, ticket_id: uuid.UUID, org_id: uuid.UUID) -> List[TicketComment]:
        result = await self.session.execute(
            select(TicketComment)
            .where(
                TicketComment.ticket_id == ticket_id,
                TicketComment.organization_id == org_id,
            )
            .order_by(TicketComment.created_at.asc())
        )
        return list(result.scalars().all())
