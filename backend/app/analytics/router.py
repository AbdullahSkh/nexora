"""Analytics API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.schemas import (
    CrmAnalytics,
    FinanceAnalytics,
    OverviewMetrics,
    ProjectsAnalytics,
)
from app.analytics.service import AnalyticsService
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.users.models import User

router = APIRouter()


def _svc(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsService:
    return AnalyticsService(db, current_user)


@router.get("/overview", response_model=OverviewMetrics)
async def get_overview_metrics(svc: AnalyticsService = Depends(_svc)):
    return await svc.get_overview()


@router.get("/crm", response_model=CrmAnalytics)
async def get_crm_analytics(svc: AnalyticsService = Depends(_svc)):
    return await svc.get_crm_analytics()


@router.get("/projects", response_model=ProjectsAnalytics)
async def get_projects_analytics(svc: AnalyticsService = Depends(_svc)):
    return await svc.get_projects_analytics()


@router.get("/finance", response_model=FinanceAnalytics)
async def get_finance_analytics(svc: AnalyticsService = Depends(_svc)):
    return await svc.get_finance_analytics()
