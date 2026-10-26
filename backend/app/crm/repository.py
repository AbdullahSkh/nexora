"""CRM repository — thin data-access layer on top of SQLAlchemy."""
from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crm.models import Activity, Company, Contact, Deal
from app.crm.schemas import (
    ActivityCreate,
    ActivityUpdate,
    CompanyCreate,
    CompanyUpdate,
    ContactCreate,
    ContactUpdate,
    DealCreate,
    DealUpdate,
)


# ---------------------------------------------------------------------------
# CompanyRepository
# ---------------------------------------------------------------------------


class CompanyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, data: CompanyCreate) -> Company:
        obj = Company(**data.model_dump(), organization_id=org_id)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, company_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Company]:
        result = await self.session.execute(
            select(Company).where(Company.id == company_id, Company.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(self, org_id: uuid.UUID) -> List[Company]:
        result = await self.session.execute(
            select(Company).where(Company.organization_id == org_id).order_by(Company.name)
        )
        return list(result.scalars().all())

    async def update(self, company: Company, data: CompanyUpdate) -> Company:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(company, field, value)
        self.session.add(company)
        await self.session.commit()
        await self.session.refresh(company)
        return company

    async def delete(self, company: Company) -> None:
        await self.session.delete(company)
        await self.session.commit()


# ---------------------------------------------------------------------------
# ContactRepository
# ---------------------------------------------------------------------------


class ContactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, data: ContactCreate) -> Contact:
        obj = Contact(**data.model_dump(), organization_id=org_id)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, contact_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Contact]:
        result = await self.session.execute(
            select(Contact).where(Contact.id == contact_id, Contact.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(self, org_id: uuid.UUID) -> List[Contact]:
        result = await self.session.execute(
            select(Contact)
            .where(Contact.organization_id == org_id)
            .order_by(Contact.last_name, Contact.first_name)
        )
        return list(result.scalars().all())

    async def update(self, contact: Contact, data: ContactUpdate) -> Contact:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(contact, field, value)
        self.session.add(contact)
        await self.session.commit()
        await self.session.refresh(contact)
        return contact

    async def delete(self, contact: Contact) -> None:
        await self.session.delete(contact)
        await self.session.commit()


# ---------------------------------------------------------------------------
# DealRepository
# ---------------------------------------------------------------------------


class DealRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, data: DealCreate) -> Deal:
        obj = Deal(**data.model_dump(), organization_id=org_id)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, deal_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Deal]:
        result = await self.session.execute(
            select(Deal).where(Deal.id == deal_id, Deal.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(self, org_id: uuid.UUID, stage: Optional[str] = None) -> List[Deal]:
        query = select(Deal).where(Deal.organization_id == org_id)
        if stage:
            query = query.where(Deal.stage == stage)
        query = query.order_by(Deal.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, deal: Deal, data: DealUpdate) -> Deal:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(deal, field, value)
        self.session.add(deal)
        await self.session.commit()
        await self.session.refresh(deal)
        return deal

    async def delete(self, deal: Deal) -> None:
        await self.session.delete(deal)
        await self.session.commit()


# ---------------------------------------------------------------------------
# ActivityRepository
# ---------------------------------------------------------------------------


class ActivityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        org_id: uuid.UUID,
        created_by_id: uuid.UUID,
        data: ActivityCreate,
    ) -> Activity:
        obj = Activity(**data.model_dump(), organization_id=org_id, created_by_id=created_by_id)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, activity_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Activity]:
        result = await self.session.execute(
            select(Activity).where(
                Activity.id == activity_id, Activity.organization_id == org_id
            )
        )
        return result.scalars().first()

    async def list(
        self,
        org_id: uuid.UUID,
        contact_id: Optional[uuid.UUID] = None,
        deal_id: Optional[uuid.UUID] = None,
    ) -> List[Activity]:
        query = select(Activity).where(Activity.organization_id == org_id)
        if contact_id:
            query = query.where(Activity.contact_id == contact_id)
        if deal_id:
            query = query.where(Activity.deal_id == deal_id)
        query = query.order_by(Activity.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, activity: Activity, data: ActivityUpdate) -> Activity:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(activity, field, value)
        self.session.add(activity)
        await self.session.commit()
        await self.session.refresh(activity)
        return activity

    async def delete(self, activity: Activity) -> None:
        await self.session.delete(activity)
        await self.session.commit()
