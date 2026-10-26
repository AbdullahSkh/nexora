"""Pydantic schemas for the Finance module."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.finance.models import ExpenseCategory, InvoiceStatus, PaymentMethod


# ---------------------------------------------------------------------------
# Invoice Line Item
# ---------------------------------------------------------------------------


class LineItemCreate(BaseModel):
    description: str
    quantity: Decimal = Decimal("1")
    unit_price: Decimal
    total: Decimal


class LineItemResponse(LineItemCreate):
    id: uuid.UUID
    invoice_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Invoice
# ---------------------------------------------------------------------------


class InvoiceBase(BaseModel):
    invoice_number: str
    status: InvoiceStatus = InvoiceStatus.DRAFT
    issue_date: date
    due_date: date
    subtotal: Decimal = Decimal("0")
    tax_rate: Decimal = Decimal("0")
    total: Decimal = Decimal("0")
    currency: str = "USD"
    notes: Optional[str] = None
    crm_company_id: Optional[uuid.UUID] = None


class InvoiceCreate(InvoiceBase):
    line_items: List[LineItemCreate] = []


class InvoiceUpdate(BaseModel):
    status: Optional[InvoiceStatus] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None
    subtotal: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    total: Optional[Decimal] = None


class InvoiceResponse(InvoiceBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    line_items: List[LineItemResponse] = []
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Expense
# ---------------------------------------------------------------------------


class ExpenseBase(BaseModel):
    category: ExpenseCategory
    description: str
    amount: Decimal
    currency: str = "USD"
    expense_date: date
    receipt_url: Optional[str] = None
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    expense_date: Optional[date] = None
    receipt_url: Optional[str] = None
    notes: Optional[str] = None


class ExpenseResponse(ExpenseBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    submitted_by_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Budget
# ---------------------------------------------------------------------------


class BudgetBase(BaseModel):
    name: str
    category: Optional[ExpenseCategory] = None
    amount: Decimal
    currency: str = "USD"
    period_start: date
    period_end: date
    notes: Optional[str] = None


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[Decimal] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    notes: Optional[str] = None


class BudgetResponse(BudgetBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------


class PaymentBase(BaseModel):
    amount: Decimal
    currency: str = "USD"
    method: PaymentMethod = PaymentMethod.BANK_TRANSFER
    payment_date: date
    reference: Optional[str] = None
    notes: Optional[str] = None
    invoice_id: Optional[uuid.UUID] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
