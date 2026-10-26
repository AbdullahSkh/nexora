"""CRM domain models: Contact, Company, Deal, Activity."""
import uuid
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Date,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class DealStage(str, Enum):
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class ActivityType(str, Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"
    TASK = "task"


# ---------------------------------------------------------------------------
# Company
# ---------------------------------------------------------------------------


class Company(Base, TimestampMixin):
    __tablename__ = "crm_companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    contacts: Mapped[list["Contact"]] = relationship(
        "Contact", back_populates="company", cascade="all, delete-orphan"
    )
    deals: Mapped[list["Deal"]] = relationship(
        "Deal", back_populates="company", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------


class Contact(Base, TimestampMixin):
    __tablename__ = "crm_contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="contacts")
    owner: Mapped[Optional["User"]] = relationship("User")  # type: ignore[name-defined]
    deals: Mapped[list["Deal"]] = relationship(
        "Deal", back_populates="contact", cascade="all, delete-orphan"
    )
    activities: Mapped[list["Activity"]] = relationship(
        "Activity", back_populates="contact", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# Deal
# ---------------------------------------------------------------------------


class Deal(Base, TimestampMixin):
    __tablename__ = "crm_deals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_contacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_companies.id", ondelete="SET NULL"),
        nullable=True,
    )
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    stage: Mapped[DealStage] = mapped_column(
        String(50), nullable=False, default=DealStage.LEAD
    )
    value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    expected_close_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    contact: Mapped[Optional["Contact"]] = relationship("Contact", back_populates="deals")
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="deals")
    owner: Mapped[Optional["User"]] = relationship("User")  # type: ignore[name-defined]
    activities: Mapped[list["Activity"]] = relationship(
        "Activity", back_populates="deal", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# Activity
# ---------------------------------------------------------------------------


class Activity(Base, TimestampMixin):
    __tablename__ = "crm_activities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_contacts.id", ondelete="CASCADE"),
        nullable=True,
    )
    deal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_deals.id", ondelete="CASCADE"),
        nullable=True,
    )
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    type: Mapped[ActivityType] = mapped_column(String(50), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    contact: Mapped[Optional["Contact"]] = relationship("Contact", back_populates="activities")
    deal: Mapped[Optional["Deal"]] = relationship("Deal", back_populates="activities")
    created_by: Mapped[Optional["User"]] = relationship("User")  # type: ignore[name-defined]
