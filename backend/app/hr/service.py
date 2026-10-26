"""HR service — business logic."""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.hr.models import Department, Employee, LeaveRequest, Position
from app.hr.repository import (
    DepartmentRepository,
    EmployeeRepository,
    LeaveRequestRepository,
    PositionRepository,
)
from app.hr.schemas import (
    DepartmentCreate,
    DepartmentUpdate,
    EmployeeCreate,
    EmployeeUpdate,
    LeaveRequestCreate,
    LeaveRequestReview,
    PositionCreate,
    PositionUpdate,
)
from app.users.models import User


def _not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


class HRService:
    def __init__(self, session: AsyncSession, current_user: User) -> None:
        self.org_id: uuid.UUID = current_user.organization_id  # type: ignore[assignment]
        self.user_id: uuid.UUID = current_user.id
        self.is_admin: bool = current_user.is_superuser
        self.dept_repo = DepartmentRepository(session)
        self.pos_repo = PositionRepository(session)
        self.emp_repo = EmployeeRepository(session)
        self.leave_repo = LeaveRequestRepository(session)

    def _require_admin(self) -> None:
        if not self.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    # ------------------------------------------------------------------
    # Departments
    # ------------------------------------------------------------------

    async def create_department(self, data: DepartmentCreate) -> Department:
        self._require_admin()
        return await self.dept_repo.create(self.org_id, data)

    async def get_department(self, dept_id: uuid.UUID) -> Department:
        obj = await self.dept_repo.get(dept_id, self.org_id)
        if not obj:
            raise _not_found("Department")
        return obj

    async def list_departments(self) -> List[Department]:
        return await self.dept_repo.list(self.org_id)

    async def update_department(self, dept_id: uuid.UUID, data: DepartmentUpdate) -> Department:
        self._require_admin()
        obj = await self.get_department(dept_id)
        return await self.dept_repo.update(obj, data)

    async def delete_department(self, dept_id: uuid.UUID) -> None:
        self._require_admin()
        obj = await self.get_department(dept_id)
        await self.dept_repo.delete(obj)

    # ------------------------------------------------------------------
    # Positions
    # ------------------------------------------------------------------

    async def create_position(self, data: PositionCreate) -> Position:
        self._require_admin()
        return await self.pos_repo.create(self.org_id, data)

    async def get_position(self, pos_id: uuid.UUID) -> Position:
        obj = await self.pos_repo.get(pos_id, self.org_id)
        if not obj:
            raise _not_found("Position")
        return obj

    async def list_positions(self) -> List[Position]:
        return await self.pos_repo.list(self.org_id)

    async def update_position(self, pos_id: uuid.UUID, data: PositionUpdate) -> Position:
        self._require_admin()
        obj = await self.get_position(pos_id)
        return await self.pos_repo.update(obj, data)

    async def delete_position(self, pos_id: uuid.UUID) -> None:
        self._require_admin()
        obj = await self.get_position(pos_id)
        await self.pos_repo.delete(obj)

    # ------------------------------------------------------------------
    # Employees
    # ------------------------------------------------------------------

    async def create_employee(self, data: EmployeeCreate) -> Employee:
        self._require_admin()
        return await self.emp_repo.create(self.org_id, data)

    async def get_employee(self, emp_id: uuid.UUID) -> Employee:
        obj = await self.emp_repo.get(emp_id, self.org_id)
        if not obj:
            raise _not_found("Employee")
        return obj

    async def list_employees(self, department_id: Optional[uuid.UUID] = None) -> List[Employee]:
        return await self.emp_repo.list(self.org_id, department_id=department_id)

    async def update_employee(self, emp_id: uuid.UUID, data: EmployeeUpdate) -> Employee:
        self._require_admin()
        obj = await self.get_employee(emp_id)
        return await self.emp_repo.update(obj, data)

    async def delete_employee(self, emp_id: uuid.UUID) -> None:
        self._require_admin()
        obj = await self.get_employee(emp_id)
        await self.emp_repo.delete(obj)

    # ------------------------------------------------------------------
    # Leave Requests
    # ------------------------------------------------------------------

    async def create_leave_request(self, data: LeaveRequestCreate) -> LeaveRequest:
        # Verify employee belongs to org
        await self.get_employee(data.employee_id)
        return await self.leave_repo.create(self.org_id, data)

    async def get_leave_request(self, lr_id: uuid.UUID) -> LeaveRequest:
        obj = await self.leave_repo.get(lr_id, self.org_id)
        if not obj:
            raise _not_found("Leave request")
        return obj

    async def list_leave_requests(
        self, employee_id: Optional[uuid.UUID] = None
    ) -> List[LeaveRequest]:
        return await self.leave_repo.list(self.org_id, employee_id=employee_id)

    async def review_leave_request(
        self, lr_id: uuid.UUID, data: LeaveRequestReview
    ) -> LeaveRequest:
        self._require_admin()
        obj = await self.get_leave_request(lr_id)
        return await self.leave_repo.review(obj, data, self.user_id)
