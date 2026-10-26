"""Pydantic schemas for Marketing module."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.marketing.models import CampaignStatus, CampaignType, LeadStatus


# ---------------------------------------------------------------------------
# Campaign Schemas
# ---------------------------------------------------------------------------


class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: CampaignType = CampaignType.EMAIL
    status: CampaignStatus = CampaignStatus.DRAFT
    budget: float = 0.0
    spend: float = 0.0
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[CampaignType] = None
    status: Optional[CampaignStatus] = None
    budget: Optional[float] = None
    spend: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CampaignResponse(CampaignBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Lead Schemas
# ---------------------------------------------------------------------------


class LeadBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    campaign_id: Optional[uuid.UUID] = None
    status: LeadStatus = LeadStatus.NEW
    score: int = 0


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    campaign_id: Optional[uuid.UUID] = None
    status: Optional[LeadStatus] = None
    score: Optional[int] = None


class LeadResponse(LeadBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
