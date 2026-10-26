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

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(orgs_router, prefix="/organizations", tags=["organizations"])
api_router.include_router(crm_router, prefix="/crm", tags=["crm"])