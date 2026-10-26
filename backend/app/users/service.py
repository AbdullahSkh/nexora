import uuid
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.schemas import UserCreate, TeamMemberCreate, UserUpdate
from app.users.repository import UserRepository
from app.users.models import User


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    def _require_admin(self, current_user: User) -> None:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can perform this action",
            )

    def _require_org(self, current_user: User) -> uuid.UUID:
        if not current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must belong to an organization",
            )
        return current_user.organization_id

    async def list_team_members(self, current_user: User) -> List[User]:
        self._require_admin(current_user)
        org_id = self._require_org(current_user)
        return await self.user_repo.list_by_organization(org_id)

    async def add_team_member(self, req: TeamMemberCreate, current_user: User) -> User:
        self._require_admin(current_user)
        org_id = self._require_org(current_user)

        existing_user = await self.user_repo.get_by_email(req.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        user_in = UserCreate(
            email=req.email,
            password=req.password,
            first_name=req.first_name,
            last_name=req.last_name,
            organization_id=org_id,
            is_superuser=req.is_superuser,
        )
        return await self.user_repo.create(user_in)

    async def update_team_member(
        self, user_id: uuid.UUID, req: UserUpdate, current_user: User
    ) -> User:
        self._require_admin(current_user)
        org_id = self._require_org(current_user)

        user = await self.user_repo.get(user_id)
        if not user or user.organization_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in your organization",
            )

        return await self.user_repo.update(user, req)

    async def deactivate_team_member(
        self, user_id: uuid.UUID, current_user: User
    ) -> None:
        self._require_admin(current_user)
        org_id = self._require_org(current_user)

        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account",
            )

        user = await self.user_repo.get(user_id)
        if not user or user.organization_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in your organization",
            )

        await self.user_repo.deactivate(user)
