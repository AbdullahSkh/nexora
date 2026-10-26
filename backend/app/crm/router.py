"""CRM API router — Companies, Contacts, Deals, Activities."""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.crm.schemas import (
    ActivityCreate,
    ActivityResponse,
    ActivityUpdate,
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
    ContactCreate,
    ContactResponse,
    ContactUpdate,
    DealCreate,
    DealResponse,
    DealUpdate,
)
from app.crm.service import CRMService
from app.users.models import User

router = APIRouter()


def _svc(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CRMService:
    return CRMService(db, current_user)


# ---------------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------------


@router.post("/companies", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(data: CompanyCreate, svc: CRMService = Depends(_svc)):
    return await svc.create_company(data)


@router.get("/companies", response_model=List[CompanyResponse])
async def list_companies(svc: CRMService = Depends(_svc)):
    return await svc.list_companies()


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: uuid.UUID, svc: CRMService = Depends(_svc)):
    return await svc.get_company(company_id)


@router.patch("/companies/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: uuid.UUID, data: CompanyUpdate, svc: CRMService = Depends(_svc)):
    return await svc.update_company(company_id, data)


@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: uuid.UUID, svc: CRMService = Depends(_svc)):
    await svc.delete_company(company_id)


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------


@router.post("/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(data: ContactCreate, svc: CRMService = Depends(_svc)):
    return await svc.create_contact(data)


@router.get("/contacts", response_model=List[ContactResponse])
async def list_contacts(svc: CRMService = Depends(_svc)):
    return await svc.list_contacts()


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: uuid.UUID, svc: CRMService = Depends(_svc)):
    return await svc.get_contact(contact_id)


@router.patch("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: uuid.UUID, data: ContactUpdate, svc: CRMService = Depends(_svc)):
    return await svc.update_contact(contact_id, data)


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: uuid.UUID, svc: CRMService = Depends(_svc)):
    await svc.delete_contact(contact_id)


# ---------------------------------------------------------------------------
# Deals
# ---------------------------------------------------------------------------


@router.post("/deals", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
async def create_deal(data: DealCreate, svc: CRMService = Depends(_svc)):
    return await svc.create_deal(data)


@router.get("/deals", response_model=List[DealResponse])
async def list_deals(
    stage: Optional[str] = Query(None, description="Filter by deal stage"),
    svc: CRMService = Depends(_svc),
):
    return await svc.list_deals(stage=stage)


@router.get("/deals/{deal_id}", response_model=DealResponse)
async def get_deal(deal_id: uuid.UUID, svc: CRMService = Depends(_svc)):
    return await svc.get_deal(deal_id)


@router.patch("/deals/{deal_id}", response_model=DealResponse)
async def update_deal(deal_id: uuid.UUID, data: DealUpdate, svc: CRMService = Depends(_svc)):
    return await svc.update_deal(deal_id, data)


@router.delete("/deals/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(deal_id: uuid.UUID, svc: CRMService = Depends(_svc)):
    await svc.delete_deal(deal_id)


# ---------------------------------------------------------------------------
# Activities
# ---------------------------------------------------------------------------


@router.post("/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(data: ActivityCreate, svc: CRMService = Depends(_svc)):
    return await svc.create_activity(data)


@router.get("/activities", response_model=List[ActivityResponse])
async def list_activities(
    contact_id: Optional[uuid.UUID] = Query(None),
    deal_id: Optional[uuid.UUID] = Query(None),
    svc: CRMService = Depends(_svc),
):
    return await svc.list_activities(contact_id=contact_id, deal_id=deal_id)


@router.get("/activities/{activity_id}", response_model=ActivityResponse)
async def get_activity(activity_id: uuid.UUID, svc: CRMService = Depends(_svc)):
    return await svc.get_activity(activity_id)


@router.patch("/activities/{activity_id}", response_model=ActivityResponse)
async def update_activity(activity_id: uuid.UUID, data: ActivityUpdate, svc: CRMService = Depends(_svc)):
    return await svc.update_activity(activity_id, data)


@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(activity_id: uuid.UUID, svc: CRMService = Depends(_svc)):
    await svc.delete_activity(activity_id)
