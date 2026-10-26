"""HR repository — data access for Department, Position, Employee, LeaveRequest."""
from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.hr.models import Department, Employee, LeaveRequest, Position
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


class DepartmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, data: DepartmentCreate) -> Department:
        obj = Department(**data.model_dump(), organization_id=org_id)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, dept_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Department]:
        result = await self.session.execute(
            select(Department).where(Department.id == dept_id, Department.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(self, org_id: uuid.UUID) -> List[Department]:
        result = await self.session.execute(
            select(Department).where(Department.organization_id == org_id).order_by(Department.name)
        )
        return list(result.scalars().all())

    async def update(self, dept: Department, data: DepartmentUpdate) -> Department:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(dept, field, value)
        self.session.add(dept)
        await self.session.commit()
        await self.session.refresh(dept)
        return dept

    async def delete(self, dept: Department) -> None:
        await self.session.delete(dept)
        await self.session.commit()


class PositionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, data: PositionCreate) -> Position:
        obj = Position(**data.model_dump(), organization_id=org_id)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, pos_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Position]:
        result = await self.session.execute(
            select(Position).where(Position.id == pos_id, Position.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(self, org_id: uuid.UUID) -> List[Position]:
        result = await self.session.execute(
            select(Position).where(Position.organization_id == org_id).order_by(Position.title)
        )
        return list(result.scalars().all())

    async def update(self, pos: Position, data: PositionUpdate) -> Position:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(pos, field, value)
        self.session.add(pos)
        await self.session.commit()
        await self.session.refresh(pos)
        return pos

    async def delete(self, pos: Position) -> None:
        await self.session.delete(pos)
        await self.session.commit()


class EmployeeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, data: EmployeeCreate) -> Employee:
        obj = Employee(**data.model_dump(), organization_id=org_id)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, emp_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Employee]:
        result = await self.session.execute(
            select(Employee).where(Employee.id == emp_id, Employee.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(self, org_id: uuid.UUID, department_id: Optional[uuid.UUID] = None) -> List[Employee]:
        query = select(Employee).where(Employee.organization_id == org_id)
        if department_id:
            query = query.where(Employee.department_id == department_id)
        result = await self.session.execute(query.order_by(Employee.last_name))
        return list(result.scalars().all())

    async def update(self, emp: Employee, data: EmployeeUpdate) -> Employee:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(emp, field, value)
        self.session.add(emp)
        await self.session.commit()
        await self.session.refresh(emp)
        return emp

    async def delete(self, emp: Employee) -> None:
        await self.session.delete(emp)
        await self.session.commit()


class LeaveRequestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, data: LeaveRequestCreate) -> LeaveRequest:
        obj = LeaveRequest(**data.model_dump(), organization_id=org_id)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, lr_id: uuid.UUID, org_id: uuid.UUID) -> Optional[LeaveRequest]:
        result = await self.session.execute(
            select(LeaveRequest).where(
                LeaveRequest.id == lr_id, LeaveRequest.organization_id == org_id
            )
        )
        return result.scalars().first()

    async def list(
        self, org_id: uuid.UUID, employee_id: Optional[uuid.UUID] = None
    ) -> List[LeaveRequest]:
        query = select(LeaveRequest).where(LeaveRequest.organization_id == org_id)
        if employee_id:
            query = query.where(LeaveRequest.employee_id == employee_id)
        result = await self.session.execute(query.order_by(LeaveRequest.start_date.desc()))
        return list(result.scalars().all())

    async def review(
        self, lr: LeaveRequest, data: LeaveRequestReview, reviewer_id: uuid.UUID
    ) -> LeaveRequest:
        lr.status = data.status
        lr.reviewer_notes = data.reviewer_notes
        lr.reviewed_by_id = reviewer_id
        self.session.add(lr)
        await self.session.commit()
        await self.session.refresh(lr)
        return lr
