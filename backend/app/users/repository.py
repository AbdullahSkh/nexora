import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_in: UserCreate) -> User:
        db_user = User(
            email=user_in.email,
            hashed_password=hash_password(user_in.password),
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            organization_id=user_in.organization_id,
            is_superuser=user_in.is_superuser,
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def get(self, user_id: uuid.UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def list_by_organization(self, org_id: uuid.UUID) -> List[User]:
        result = await self.session.execute(
            select(User).where(User.organization_id == org_id).order_by(User.created_at)
        )
        return list(result.scalars().all())

    async def update(self, user: User, user_update: UserUpdate) -> User:
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def deactivate(self, user: User) -> None:
        user.is_active = False
        self.session.add(user)
        await self.session.commit()
