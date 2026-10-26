"""Pydantic schemas for the HR module."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.hr.models import EmployeeStatus, EmploymentType, LeaveStatus, LeaveType


# ---------------------------------------------------------------------------
# Department
# ---------------------------------------------------------------------------


class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class DepartmentResponse(DepartmentBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Position
# ---------------------------------------------------------------------------


class PositionBase(BaseModel):
    title: str
    description: Optional[str] = None


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class PositionResponse(PositionBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------


class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    hire_date: Optional[date] = None
    salary: Optional[float] = None
    currency: str = "USD"
    department_id: Optional[uuid.UUID] = None
    position_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    status: Optional[EmployeeStatus] = None
    hire_date: Optional[date] = None
    termination_date: Optional[date] = None
    salary: Optional[float] = None
    currency: Optional[str] = None
    department_id: Optional[uuid.UUID] = None
    position_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None


class EmployeeResponse(EmployeeBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    termination_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Leave Request
# ---------------------------------------------------------------------------


class LeaveRequestBase(BaseModel):
    type: LeaveType
    start_date: date
    end_date: date
    reason: Optional[str] = None


class LeaveRequestCreate(LeaveRequestBase):
    employee_id: uuid.UUID


class LeaveRequestReview(BaseModel):
    status: LeaveStatus
    reviewer_notes: Optional[str] = None


class LeaveRequestResponse(LeaveRequestBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    status: LeaveStatus
    reviewed_by_id: Optional[uuid.UUID] = None
    reviewer_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
