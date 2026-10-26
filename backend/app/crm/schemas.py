"""Pydantic schemas for the CRM module."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.crm.models import ActivityType, DealStage


# ---------------------------------------------------------------------------
# Company
# ---------------------------------------------------------------------------


class CompanyBase(BaseModel):
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class CompanyResponse(CompanyBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    notes: Optional[str] = None
    company_id: Optional[uuid.UUID] = None
    owner_id: Optional[uuid.UUID] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    notes: Optional[str] = None
    company_id: Optional[uuid.UUID] = None
    owner_id: Optional[uuid.UUID] = None


class ContactResponse(ContactBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Deal
# ---------------------------------------------------------------------------


class DealBase(BaseModel):
    title: str
    stage: DealStage = DealStage.LEAD
    value: Optional[Decimal] = None
    currency: str = "USD"
    expected_close_date: Optional[date] = None
    notes: Optional[str] = None
    contact_id: Optional[uuid.UUID] = None
    company_id: Optional[uuid.UUID] = None
    owner_id: Optional[uuid.UUID] = None


class DealCreate(DealBase):
    pass


class DealUpdate(BaseModel):
    title: Optional[str] = None
    stage: Optional[DealStage] = None
    value: Optional[Decimal] = None
    currency: Optional[str] = None
    expected_close_date: Optional[date] = None
    notes: Optional[str] = None
    contact_id: Optional[uuid.UUID] = None
    company_id: Optional[uuid.UUID] = None
    owner_id: Optional[uuid.UUID] = None


class DealResponse(DealBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Activity
# ---------------------------------------------------------------------------


class ActivityBase(BaseModel):
    type: ActivityType
    subject: str
    body: Optional[str] = None
    due_date: Optional[date] = None
    contact_id: Optional[uuid.UUID] = None
    deal_id: Optional[uuid.UUID] = None


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    type: Optional[ActivityType] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    due_date: Optional[date] = None
    contact_id: Optional[uuid.UUID] = None
    deal_id: Optional[uuid.UUID] = None


class ActivityResponse(ActivityBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
