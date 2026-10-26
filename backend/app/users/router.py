import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.users.schemas import UserResponse, TeamMemberCreate, UserUpdate
from app.users.models import User
from app.users.service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return current_user


@router.get("/", response_model=List[UserResponse])
async def list_team_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all team members in the current user's organization. Requires admin."""
    service = UserService(db)
    return await service.list_team_members(current_user)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_team_member(
    req: TeamMemberCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a new team member to the current user's organization. Requires admin."""
    service = UserService(db)
    return await service.add_team_member(req, current_user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_team_member(
    user_id: uuid.UUID,
    req: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a team member's profile. Requires admin."""
    service = UserService(db)
    return await service.update_team_member(user_id, req, current_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_member(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a team member. Requires admin."""
    service = UserService(db)
    await service.deactivate_team_member(user_id, current_user)
