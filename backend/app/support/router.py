"""Customer Support API router."""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.support.schemas import (
    CommentCreate,
    CommentResponse,
    TicketCreate,
    TicketDetailResponse,
    TicketResponse,
    TicketUpdate,
)
from app.support.service import SupportService
from app.users.models import User

router = APIRouter()


def _svc(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SupportService:
    return SupportService(db, current_user)


# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(data: TicketCreate, svc: SupportService = Depends(_svc)):
    return await svc.create_ticket(data)


@router.get("/", response_model=List[TicketResponse])
async def list_tickets(
    ticket_status: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = Query(None),
    assigned_to_id: Optional[uuid.UUID] = Query(None),
    search: Optional[str] = Query(None),
    svc: SupportService = Depends(_svc),
):
    return await svc.list_tickets(
        status=ticket_status,
        priority=priority,
        assigned_to_id=assigned_to_id,
        search=search,
    )


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket(ticket_id: uuid.UUID, svc: SupportService = Depends(_svc)):
    return await svc.get_ticket(ticket_id)


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: uuid.UUID,
    data: TicketUpdate,
    svc: SupportService = Depends(_svc),
):
    return await svc.update_ticket(ticket_id, data)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(ticket_id: uuid.UUID, svc: SupportService = Depends(_svc)):
    await svc.delete_ticket(ticket_id)


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------


@router.post(
    "/{ticket_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_comment(
    ticket_id: uuid.UUID,
    data: CommentCreate,
    svc: SupportService = Depends(_svc),
):
    return await svc.add_comment(ticket_id, data)


@router.get("/{ticket_id}/comments", response_model=List[CommentResponse])
async def list_comments(ticket_id: uuid.UUID, svc: SupportService = Depends(_svc)):
    return await svc.list_comments(ticket_id)
