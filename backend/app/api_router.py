"""Central API router registration.

Each milestone registers its routers here as modules come online.
Routers are added incrementally; unimplemented modules are not registered
until their milestone is reached.
"""

from fastapi import APIRouter
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.organizations.router import router as orgs_router
from app.crm.router import router as crm_router
from app.hr.router import router as hr_router
from app.projects.router import router as projects_router
from app.finance.router import router as finance_router
from app.documents.router import router as documents_router
from app.meetings.router import router as meetings_router
from app.support.router import router as support_router
from app.notifications.router import router as notifications_router
from app.marketing.router import router as marketing_router
from app.analytics.router import router as analytics_router
from app.ai.router import router as ai_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(orgs_router, prefix="/organizations", tags=["organizations"])
api_router.include_router(crm_router, prefix="/crm", tags=["crm"])
api_router.include_router(hr_router, prefix="/hr", tags=["hr"])
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(finance_router, prefix="/finance", tags=["finance"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(meetings_router, prefix="/meetings", tags=["meetings"])
api_router.include_router(support_router, prefix="/support", tags=["support"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
api_router.include_router(marketing_router, prefix="/marketing", tags=["marketing"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])