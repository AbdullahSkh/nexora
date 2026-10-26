from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_organization
from app.organizations.schemas import OrganizationResponse
from app.organizations.repository import OrganizationRepository
import uuid

router = APIRouter()

@router.get("/me", response_model=OrganizationResponse)
async def read_organization_me(
    org_id: uuid.UUID = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get the currently authenticated user's organization."""
    org_repo = OrganizationRepository(db)
    org = await org_repo.get(org_id)
    return org
