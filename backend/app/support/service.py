"""Support service — business logic."""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.support.models import Ticket, TicketComment
from app.support.repository import TicketCommentRepository, TicketRepository
from app.support.schemas import CommentCreate, TicketCreate, TicketUpdate
from app.users.models import User


def _not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


class SupportService:
    def __init__(self, session: AsyncSession, current_user: User) -> None:
        self.org_id: uuid.UUID = current_user.organization_id  # type: ignore[assignment]
        self.user_id: uuid.UUID = current_user.id
        self.ticket_repo = TicketRepository(session)
        self.comment_repo = TicketCommentRepository(session)

    # ------------------------------------------------------------------
    # Tickets
    # ------------------------------------------------------------------

    async def create_ticket(self, data: TicketCreate) -> Ticket:
        return await self.ticket_repo.create(self.org_id, self.user_id, data)

    async def get_ticket(self, ticket_id: uuid.UUID) -> Ticket:
        ticket = await self.ticket_repo.get(ticket_id, self.org_id)
        if not ticket:
            raise _not_found("Ticket")
        return ticket

    async def list_tickets(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
    ) -> List[Ticket]:
        return await self.ticket_repo.list(
            self.org_id,
            status=status,
            priority=priority,
            assigned_to_id=assigned_to_id,
            search=search,
        )

    async def update_ticket(self, ticket_id: uuid.UUID, data: TicketUpdate) -> Ticket:
        ticket = await self.get_ticket(ticket_id)
        return await self.ticket_repo.update(ticket, data)

    async def delete_ticket(self, ticket_id: uuid.UUID) -> None:
        ticket = await self.get_ticket(ticket_id)
        await self.ticket_repo.delete(ticket)

    # ------------------------------------------------------------------
    # Comments
    # ------------------------------------------------------------------

    async def add_comment(self, ticket_id: uuid.UUID, data: CommentCreate) -> TicketComment:
        await self.get_ticket(ticket_id)
        return await self.comment_repo.create(self.org_id, ticket_id, self.user_id, data)

    async def list_comments(self, ticket_id: uuid.UUID) -> List[TicketComment]:
        await self.get_ticket(ticket_id)
        return await self.comment_repo.list(ticket_id, self.org_id)
