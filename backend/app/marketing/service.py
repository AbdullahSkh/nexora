"""Marketing service — business logic."""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.marketing.models import MarketingCampaign, MarketingLead
from app.marketing.repository import CampaignRepository, LeadRepository
from app.marketing.schemas import (
    CampaignCreate,
    CampaignUpdate,
    LeadCreate,
    LeadUpdate,
)
from app.users.models import User


def _not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


class MarketingService:
    def __init__(self, session: AsyncSession, current_user: User) -> None:
        self.org_id: uuid.UUID = current_user.organization_id  # type: ignore[assignment]
        self.user_id: uuid.UUID = current_user.id
        self.campaign_repo = CampaignRepository(session)
        self.lead_repo = LeadRepository(session)

    # ------------------------------------------------------------------
    # Campaigns
    # ------------------------------------------------------------------

    async def create_campaign(self, data: CampaignCreate) -> MarketingCampaign:
        return await self.campaign_repo.create(self.org_id, self.user_id, data)

    async def get_campaign(self, campaign_id: uuid.UUID) -> MarketingCampaign:
        camp = await self.campaign_repo.get(campaign_id, self.org_id)
        if not camp:
            raise _not_found("Marketing campaign")
        return camp

    async def list_campaigns(
        self,
        status: Optional[str] = None,
        campaign_type: Optional[str] = None,
    ) -> List[MarketingCampaign]:
        return await self.campaign_repo.list(
            self.org_id, status=status, campaign_type=campaign_type
        )

    async def update_campaign(
        self, campaign_id: uuid.UUID, data: CampaignUpdate
    ) -> MarketingCampaign:
        camp = await self.get_campaign(campaign_id)
        return await self.campaign_repo.update(camp, data)

    async def delete_campaign(self, campaign_id: uuid.UUID) -> None:
        camp = await self.get_campaign(campaign_id)
        await self.campaign_repo.delete(camp)

    # ------------------------------------------------------------------
    # Leads
    # ------------------------------------------------------------------

    async def create_lead(self, data: LeadCreate) -> MarketingLead:
        if data.campaign_id:
            await self.get_campaign(data.campaign_id)
        return await self.lead_repo.create(self.org_id, self.user_id, data)

    async def get_lead(self, lead_id: uuid.UUID) -> MarketingLead:
        lead = await self.lead_repo.get(lead_id, self.org_id)
        if not lead:
            raise _not_found("Marketing lead")
        return lead

    async def list_leads(
        self,
        campaign_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[MarketingLead]:
        return await self.lead_repo.list(
            self.org_id, campaign_id=campaign_id, status=status, search=search
        )

    async def update_lead(self, lead_id: uuid.UUID, data: LeadUpdate) -> MarketingLead:
        lead = await self.get_lead(lead_id)
        if data.campaign_id:
            await self.get_campaign(data.campaign_id)
        return await self.lead_repo.update(lead, data)

    async def delete_lead(self, lead_id: uuid.UUID) -> None:
        lead = await self.get_lead(lead_id)
        await self.lead_repo.delete(lead)
