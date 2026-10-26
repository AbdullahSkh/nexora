"""Marketing repository — data access layer."""
from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.marketing.models import MarketingCampaign, MarketingLead
from app.marketing.schemas import (
    CampaignCreate,
    CampaignUpdate,
    LeadCreate,
    LeadUpdate,
)


class CampaignRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self, org_id: uuid.UUID, user_id: Optional[uuid.UUID], data: CampaignCreate
    ) -> MarketingCampaign:
        camp = MarketingCampaign(
            **data.model_dump(),
            organization_id=org_id,
            created_by_id=user_id,
        )
        self.session.add(camp)
        await self.session.commit()
        await self.session.refresh(camp)
        return camp

    async def get(
        self, campaign_id: uuid.UUID, org_id: uuid.UUID
    ) -> Optional[MarketingCampaign]:
        result = await self.session.execute(
            select(MarketingCampaign).where(
                MarketingCampaign.id == campaign_id,
                MarketingCampaign.organization_id == org_id,
            )
        )
        return result.scalars().first()

    async def list(
        self,
        org_id: uuid.UUID,
        status: Optional[str] = None,
        campaign_type: Optional[str] = None,
    ) -> List[MarketingCampaign]:
        q = select(MarketingCampaign).where(MarketingCampaign.organization_id == org_id)
        if status:
            q = q.where(MarketingCampaign.status == status)
        if campaign_type:
            q = q.where(MarketingCampaign.type == campaign_type)
        result = await self.session.execute(q.order_by(MarketingCampaign.created_at.desc()))
        return list(result.scalars().all())

    async def update(
        self, campaign: MarketingCampaign, data: CampaignUpdate
    ) -> MarketingCampaign:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(campaign, field, value)
        self.session.add(campaign)
        await self.session.commit()
        await self.session.refresh(campaign)
        return campaign

    async def delete(self, campaign: MarketingCampaign) -> None:
        await self.session.delete(campaign)
        await self.session.commit()


class LeadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self, org_id: uuid.UUID, user_id: Optional[uuid.UUID], data: LeadCreate
    ) -> MarketingLead:
        lead = MarketingLead(
            **data.model_dump(),
            organization_id=org_id,
            created_by_id=user_id,
        )
        self.session.add(lead)
        await self.session.commit()
        await self.session.refresh(lead)
        return lead

    async def get(self, lead_id: uuid.UUID, org_id: uuid.UUID) -> Optional[MarketingLead]:
        result = await self.session.execute(
            select(MarketingLead).where(
                MarketingLead.id == lead_id,
                MarketingLead.organization_id == org_id,
            )
        )
        return result.scalars().first()

    async def list(
        self,
        org_id: uuid.UUID,
        campaign_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[MarketingLead]:
        q = select(MarketingLead).where(MarketingLead.organization_id == org_id)
        if campaign_id:
            q = q.where(MarketingLead.campaign_id == campaign_id)
        if status:
            q = q.where(MarketingLead.status == status)
        if search:
            pat = f"%{search}%"
            q = q.where(
                or_(
                    MarketingLead.email.ilike(pat),
                    MarketingLead.first_name.ilike(pat),
                    MarketingLead.last_name.ilike(pat),
                    MarketingLead.company.ilike(pat),
                )
            )
        result = await self.session.execute(q.order_by(MarketingLead.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, lead: MarketingLead, data: LeadUpdate) -> MarketingLead:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(lead, field, value)
        self.session.add(lead)
        await self.session.commit()
        await self.session.refresh(lead)
        return lead

    async def delete(self, lead: MarketingLead) -> None:
        await self.session.delete(lead)
        await self.session.commit()
