"""HR domain models: Department, Employee, Position, LeaveRequest."""
from __future__ import annotations

import uuid
from datetime import date
from enum import Enum
from typing import Optional

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERN = "intern"


class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"


class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveType(str, Enum):
    ANNUAL = "annual"
    SICK = "sick"
    UNPAID = "unpaid"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    OTHER = "other"


# ---------------------------------------------------------------------------
# Department
# ---------------------------------------------------------------------------


class Department(Base, TimestampMixin):
    __tablename__ = "hr_departments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    employees: Mapped[list["Employee"]] = relationship(
        "Employee", back_populates="department", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# Position / Job Title
# ---------------------------------------------------------------------------


class Position(Base, TimestampMixin):
    __tablename__ = "hr_positions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    employees: Mapped[list["Employee"]] = relationship(
        "Employee", back_populates="position"
    )


# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------


class Employee(Base, TimestampMixin):
    __tablename__ = "hr_employees"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True, unique=True
    )
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hr_departments.id", ondelete="SET NULL"),
        nullable=True
    )
    position_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hr_positions.id", ondelete="SET NULL"),
        nullable=True
    )
    manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hr_employees.id", ondelete="SET NULL"),
        nullable=True
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    employment_type: Mapped[EmploymentType] = mapped_column(
        String(50), nullable=False, default=EmploymentType.FULL_TIME
    )
    status: Mapped[EmployeeStatus] = mapped_column(
        String(50), nullable=False, default=EmployeeStatus.ACTIVE
    )
    hire_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    termination_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    salary: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="employees")
    position: Mapped[Optional["Position"]] = relationship("Position", back_populates="employees")
    manager: Mapped[Optional["Employee"]] = relationship("Employee", remote_side="Employee.id")
    leave_requests: Mapped[list["LeaveRequest"]] = relationship(
        "LeaveRequest", back_populates="employee", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# Leave Request
# ---------------------------------------------------------------------------


class LeaveRequest(Base, TimestampMixin):
    __tablename__ = "hr_leave_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hr_employees.id", ondelete="CASCADE"),
        nullable=False
    )
    reviewed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    type: Mapped[LeaveType] = mapped_column(String(50), nullable=False)
    status: Mapped[LeaveStatus] = mapped_column(
        String(50), nullable=False, default=LeaveStatus.PENDING
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    employee: Mapped["Employee"] = relationship("Employee", back_populates="leave_requests")
    reviewed_by: Mapped[Optional["User"]] = relationship("User")  # type: ignore[name-defined]
