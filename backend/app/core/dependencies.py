"""Common FastAPI dependencies.

Full auth dependencies (get_current_user, get_current_organization,
require_permission) are implemented in Milestone 2 when the auth module
exists. Milestone 1 exposes the database dependency only.
"""

from collections.abc import AsyncIterator
import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException
from app.users.repository import UserRepository
from app.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Alias dependency for database sessions."""
    async for session in get_db():
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """Dependency to get the current authenticated user."""
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Could not validate credentials")
    
    user_repo = UserRepository(db)
    user = await user_repo.get(uuid.UUID(user_id))
    if not user:
        raise UnauthorizedException("User not found")
    if not user.is_active:
        raise UnauthorizedException("Inactive user")
    return user

async def get_current_organization(user: User = Depends(get_current_user)) -> uuid.UUID:
    """Dependency to ensure and get the current user's organization."""
    if not user.organization_id:
        raise UnauthorizedException("User does not belong to any organization")
    return user.organization_id