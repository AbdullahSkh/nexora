"""Marketing API router."""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.marketing.schemas import (
    CampaignCreate,
    CampaignResponse,
    CampaignUpdate,
    LeadCreate,
    LeadResponse,
    LeadUpdate,
)
from app.marketing.service import MarketingService
from app.users.models import User

router = APIRouter()


def _svc(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MarketingService:
    return MarketingService(db, current_user)


# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------


@router.post("/campaigns", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(data: CampaignCreate, svc: MarketingService = Depends(_svc)):
    return await svc.create_campaign(data)


@router.get("/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(
    campaign_status: Optional[str] = Query(None, alias="status"),
    campaign_type: Optional[str] = Query(None, alias="type"),
    svc: MarketingService = Depends(_svc),
):
    return await svc.list_campaigns(status=campaign_status, campaign_type=campaign_type)


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: uuid.UUID, svc: MarketingService = Depends(_svc)):
    return await svc.get_campaign(campaign_id)


@router.patch("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: uuid.UUID,
    data: CampaignUpdate,
    svc: MarketingService = Depends(_svc),
):
    return await svc.update_campaign(campaign_id, data)


@router.delete("/campaigns/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(campaign_id: uuid.UUID, svc: MarketingService = Depends(_svc)):
    await svc.delete_campaign(campaign_id)


# ---------------------------------------------------------------------------
# Leads
# ---------------------------------------------------------------------------


@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(data: LeadCreate, svc: MarketingService = Depends(_svc)):
    return await svc.create_lead(data)


@router.get("/leads", response_model=List[LeadResponse])
async def list_leads(
    campaign_id: Optional[uuid.UUID] = Query(None),
    lead_status: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    svc: MarketingService = Depends(_svc),
):
    return await svc.list_leads(
        campaign_id=campaign_id,
        status=lead_status,
        search=search,
    )


@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: uuid.UUID, svc: MarketingService = Depends(_svc)):
    return await svc.get_lead(lead_id)


@router.patch("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: uuid.UUID,
    data: LeadUpdate,
    svc: MarketingService = Depends(_svc),
):
    return await svc.update_lead(lead_id, data)


@router.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(lead_id: uuid.UUID, svc: MarketingService = Depends(_svc)):
    await svc.delete_lead(lead_id)
