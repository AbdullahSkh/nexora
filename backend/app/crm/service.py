"""CRM service — business logic and authorization."""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crm.models import Activity, Company, Contact, Deal
from app.crm.repository import (
    ActivityRepository,
    CompanyRepository,
    ContactRepository,
    DealRepository,
)
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
from app.users.models import User


def _not_found(resource: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found",
    )


class CRMService:
    def __init__(self, session: AsyncSession, current_user: User) -> None:
        self.org_id: uuid.UUID = current_user.organization_id  # type: ignore[assignment]
        self.user_id: uuid.UUID = current_user.id
        self.company_repo = CompanyRepository(session)
        self.contact_repo = ContactRepository(session)
        self.deal_repo = DealRepository(session)
        self.activity_repo = ActivityRepository(session)

    # ------------------------------------------------------------------
    # Companies
    # ------------------------------------------------------------------

    async def create_company(self, data: CompanyCreate) -> Company:
        return await self.company_repo.create(self.org_id, data)

    async def get_company(self, company_id: uuid.UUID) -> Company:
        obj = await self.company_repo.get(company_id, self.org_id)
        if not obj:
            raise _not_found("Company")
        return obj

    async def list_companies(self) -> List[Company]:
        return await self.company_repo.list(self.org_id)

    async def update_company(self, company_id: uuid.UUID, data: CompanyUpdate) -> Company:
        obj = await self.get_company(company_id)
        return await self.company_repo.update(obj, data)

    async def delete_company(self, company_id: uuid.UUID) -> None:
        obj = await self.get_company(company_id)
        await self.company_repo.delete(obj)

    # ------------------------------------------------------------------
    # Contacts
    # ------------------------------------------------------------------

    async def create_contact(self, data: ContactCreate) -> Contact:
        return await self.contact_repo.create(self.org_id, data)

    async def get_contact(self, contact_id: uuid.UUID) -> Contact:
        obj = await self.contact_repo.get(contact_id, self.org_id)
        if not obj:
            raise _not_found("Contact")
        return obj

    async def list_contacts(self) -> List[Contact]:
        return await self.contact_repo.list(self.org_id)

    async def update_contact(self, contact_id: uuid.UUID, data: ContactUpdate) -> Contact:
        obj = await self.get_contact(contact_id)
        return await self.contact_repo.update(obj, data)

    async def delete_contact(self, contact_id: uuid.UUID) -> None:
        obj = await self.get_contact(contact_id)
        await self.contact_repo.delete(obj)

    # ------------------------------------------------------------------
    # Deals
    # ------------------------------------------------------------------

    async def create_deal(self, data: DealCreate) -> Deal:
        return await self.deal_repo.create(self.org_id, data)

    async def get_deal(self, deal_id: uuid.UUID) -> Deal:
        obj = await self.deal_repo.get(deal_id, self.org_id)
        if not obj:
            raise _not_found("Deal")
        return obj

    async def list_deals(self, stage: Optional[str] = None) -> List[Deal]:
        return await self.deal_repo.list(self.org_id, stage=stage)

    async def update_deal(self, deal_id: uuid.UUID, data: DealUpdate) -> Deal:
        obj = await self.get_deal(deal_id)
        return await self.deal_repo.update(obj, data)

    async def delete_deal(self, deal_id: uuid.UUID) -> None:
        obj = await self.get_deal(deal_id)
        await self.deal_repo.delete(obj)

    # ------------------------------------------------------------------
    # Activities
    # ------------------------------------------------------------------

    async def create_activity(self, data: ActivityCreate) -> Activity:
        return await self.activity_repo.create(self.org_id, self.user_id, data)

    async def get_activity(self, activity_id: uuid.UUID) -> Activity:
        obj = await self.activity_repo.get(activity_id, self.org_id)
        if not obj:
            raise _not_found("Activity")
        return obj

    async def list_activities(
        self,
        contact_id: Optional[uuid.UUID] = None,
        deal_id: Optional[uuid.UUID] = None,
    ) -> List[Activity]:
        return await self.activity_repo.list(self.org_id, contact_id=contact_id, deal_id=deal_id)

    async def update_activity(self, activity_id: uuid.UUID, data: ActivityUpdate) -> Activity:
        obj = await self.get_activity(activity_id)
        return await self.activity_repo.update(obj, data)

    async def delete_activity(self, activity_id: uuid.UUID) -> None:
        obj = await self.get_activity(activity_id)
        await self.activity_repo.delete(obj)
