from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.schemas import RegisterRequest, LoginRequest, Token
from app.organizations.schemas import OrganizationCreate
from app.organizations.repository import OrganizationRepository
from app.users.schemas import UserCreate
from app.users.repository import UserRepository
from app.core.security import verify_password, create_access_token

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.org_repo = OrganizationRepository(session)
        self.user_repo = UserRepository(session)

    async def register(self, req: RegisterRequest) -> Token:
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(req.user_email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        
        # Check if organization exists
        org = await self.org_repo.get_by_name(req.organization_name)
        is_first_user = False
        
        if not org:
            # Create organization if it doesn't exist
            org_in = OrganizationCreate(name=req.organization_name)
            org = await self.org_repo.create(org_in)
            is_first_user = True  # First user of a new org gets admin role
        
        # Create user
        user_in = UserCreate(
            email=req.user_email,
            password=req.password,
            first_name=req.first_name,
            last_name=req.last_name,
            organization_id=org.id,
            is_superuser=is_first_user
        )
        user = await self.user_repo.create(user_in)
        
        # Create token
        access_token = create_access_token(
            subject=str(user.id),
            organization_id=str(org.id)
        )
        return Token(access_token=access_token)

    async def login(self, req: LoginRequest) -> Token:
        user = await self.user_repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        
        access_token = create_access_token(
            subject=str(user.id),
            organization_id=str(user.organization_id) if user.organization_id else None
        )
        return Token(access_token=access_token)
