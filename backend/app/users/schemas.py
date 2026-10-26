from pydantic import BaseModel, EmailStr, ConfigDict
import uuid
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    organization_id: Optional[uuid.UUID] = None
    is_superuser: bool = False

class TeamMemberCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_superuser: bool = False

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    organization_id: Optional[uuid.UUID]

    model_config = ConfigDict(from_attributes=True)
