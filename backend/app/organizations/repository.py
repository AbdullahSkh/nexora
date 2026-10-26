import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.organizations.models import Organization
from app.organizations.schemas import OrganizationCreate

class OrganizationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, org_in: OrganizationCreate) -> Organization:
        db_org = Organization(name=org_in.name)
        self.session.add(db_org)
        await self.session.commit()
        await self.session.refresh(db_org)
        return db_org

    async def get(self, org_id: uuid.UUID) -> Organization | None:
        return await self.session.get(Organization, org_id)

    async def get_by_name(self, name: str) -> Organization | None:
        result = await self.session.execute(select(Organization).where(Organization.name == name))
        return result.scalars().first()
