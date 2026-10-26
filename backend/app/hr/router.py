"""HR API router — Departments, Positions, Employees, Leave Requests."""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.hr.schemas import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveRequestReview,
    PositionCreate,
    PositionResponse,
    PositionUpdate,
)
from app.hr.service import HRService
from app.users.models import User

router = APIRouter()


def _svc(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HRService:
    return HRService(db, current_user)


# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------


@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(data: DepartmentCreate, svc: HRService = Depends(_svc)):
    return await svc.create_department(data)


@router.get("/departments", response_model=List[DepartmentResponse])
async def list_departments(svc: HRService = Depends(_svc)):
    return await svc.list_departments()


@router.get("/departments/{dept_id}", response_model=DepartmentResponse)
async def get_department(dept_id: uuid.UUID, svc: HRService = Depends(_svc)):
    return await svc.get_department(dept_id)


@router.patch("/departments/{dept_id}", response_model=DepartmentResponse)
async def update_department(dept_id: uuid.UUID, data: DepartmentUpdate, svc: HRService = Depends(_svc)):
    return await svc.update_department(dept_id, data)


@router.delete("/departments/{dept_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(dept_id: uuid.UUID, svc: HRService = Depends(_svc)):
    await svc.delete_department(dept_id)


# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------


@router.post("/positions", response_model=PositionResponse, status_code=status.HTTP_201_CREATED)
async def create_position(data: PositionCreate, svc: HRService = Depends(_svc)):
    return await svc.create_position(data)


@router.get("/positions", response_model=List[PositionResponse])
async def list_positions(svc: HRService = Depends(_svc)):
    return await svc.list_positions()


@router.get("/positions/{pos_id}", response_model=PositionResponse)
async def get_position(pos_id: uuid.UUID, svc: HRService = Depends(_svc)):
    return await svc.get_position(pos_id)


@router.patch("/positions/{pos_id}", response_model=PositionResponse)
async def update_position(pos_id: uuid.UUID, data: PositionUpdate, svc: HRService = Depends(_svc)):
    return await svc.update_position(pos_id, data)


@router.delete("/positions/{pos_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(pos_id: uuid.UUID, svc: HRService = Depends(_svc)):
    await svc.delete_position(pos_id)


# ---------------------------------------------------------------------------
# Employees
# ---------------------------------------------------------------------------


@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(data: EmployeeCreate, svc: HRService = Depends(_svc)):
    return await svc.create_employee(data)


@router.get("/employees", response_model=List[EmployeeResponse])
async def list_employees(
    department_id: Optional[uuid.UUID] = Query(None, description="Filter by department"),
    svc: HRService = Depends(_svc),
):
    return await svc.list_employees(department_id=department_id)


@router.get("/employees/{emp_id}", response_model=EmployeeResponse)
async def get_employee(emp_id: uuid.UUID, svc: HRService = Depends(_svc)):
    return await svc.get_employee(emp_id)


@router.patch("/employees/{emp_id}", response_model=EmployeeResponse)
async def update_employee(emp_id: uuid.UUID, data: EmployeeUpdate, svc: HRService = Depends(_svc)):
    return await svc.update_employee(emp_id, data)


@router.delete("/employees/{emp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(emp_id: uuid.UUID, svc: HRService = Depends(_svc)):
    await svc.delete_employee(emp_id)


# ---------------------------------------------------------------------------
# Leave Requests
# ---------------------------------------------------------------------------


@router.post("/leave-requests", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_request(data: LeaveRequestCreate, svc: HRService = Depends(_svc)):
    return await svc.create_leave_request(data)


@router.get("/leave-requests", response_model=List[LeaveRequestResponse])
async def list_leave_requests(
    employee_id: Optional[uuid.UUID] = Query(None),
    svc: HRService = Depends(_svc),
):
    return await svc.list_leave_requests(employee_id=employee_id)


@router.get("/leave-requests/{lr_id}", response_model=LeaveRequestResponse)
async def get_leave_request(lr_id: uuid.UUID, svc: HRService = Depends(_svc)):
    return await svc.get_leave_request(lr_id)


@router.post("/leave-requests/{lr_id}/review", response_model=LeaveRequestResponse)
async def review_leave_request(lr_id: uuid.UUID, data: LeaveRequestReview, svc: HRService = Depends(_svc)):
    return await svc.review_leave_request(lr_id, data)
