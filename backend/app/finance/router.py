"""Finance API router."""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.finance.schemas import (
    BudgetCreate, BudgetResponse, BudgetUpdate,
    ExpenseCreate, ExpenseResponse, ExpenseUpdate,
    InvoiceCreate, InvoiceResponse, InvoiceUpdate,
    PaymentCreate, PaymentResponse,
)
from app.finance.service import FinanceService
from app.users.models import User

router = APIRouter()


def _svc(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FinanceService:
    return FinanceService(db, current_user)


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(data: InvoiceCreate, svc: FinanceService = Depends(_svc)):
    return await svc.create_invoice(data)


@router.get("/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    invoice_status: Optional[str] = Query(None, alias="status"),
    svc: FinanceService = Depends(_svc),
):
    return await svc.list_invoices(status=invoice_status)


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: uuid.UUID, svc: FinanceService = Depends(_svc)):
    return await svc.get_invoice(invoice_id)


@router.patch("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(invoice_id: uuid.UUID, data: InvoiceUpdate, svc: FinanceService = Depends(_svc)):
    return await svc.update_invoice(invoice_id, data)


@router.delete("/invoices/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(invoice_id: uuid.UUID, svc: FinanceService = Depends(_svc)):
    await svc.delete_invoice(invoice_id)


# ---------------------------------------------------------------------------
# Expenses
# ---------------------------------------------------------------------------


@router.post("/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(data: ExpenseCreate, svc: FinanceService = Depends(_svc)):
    return await svc.create_expense(data)


@router.get("/expenses", response_model=List[ExpenseResponse])
async def list_expenses(
    category: Optional[str] = Query(None),
    svc: FinanceService = Depends(_svc),
):
    return await svc.list_expenses(category=category)


@router.get("/expenses/{expense_id}", response_model=ExpenseResponse)
async def get_expense(expense_id: uuid.UUID, svc: FinanceService = Depends(_svc)):
    return await svc.get_expense(expense_id)


@router.patch("/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense(expense_id: uuid.UUID, data: ExpenseUpdate, svc: FinanceService = Depends(_svc)):
    return await svc.update_expense(expense_id, data)


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(expense_id: uuid.UUID, svc: FinanceService = Depends(_svc)):
    await svc.delete_expense(expense_id)


# ---------------------------------------------------------------------------
# Budgets
# ---------------------------------------------------------------------------


@router.post("/budgets", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(data: BudgetCreate, svc: FinanceService = Depends(_svc)):
    return await svc.create_budget(data)


@router.get("/budgets", response_model=List[BudgetResponse])
async def list_budgets(svc: FinanceService = Depends(_svc)):
    return await svc.list_budgets()


@router.get("/budgets/{budget_id}", response_model=BudgetResponse)
async def get_budget(budget_id: uuid.UUID, svc: FinanceService = Depends(_svc)):
    return await svc.get_budget(budget_id)


@router.patch("/budgets/{budget_id}", response_model=BudgetResponse)
async def update_budget(budget_id: uuid.UUID, data: BudgetUpdate, svc: FinanceService = Depends(_svc)):
    return await svc.update_budget(budget_id, data)


@router.delete("/budgets/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(budget_id: uuid.UUID, svc: FinanceService = Depends(_svc)):
    await svc.delete_budget(budget_id)


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------


@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(data: PaymentCreate, svc: FinanceService = Depends(_svc)):
    return await svc.create_payment(data)


@router.get("/payments", response_model=List[PaymentResponse])
async def list_payments(
    invoice_id: Optional[uuid.UUID] = Query(None),
    svc: FinanceService = Depends(_svc),
):
    return await svc.list_payments(invoice_id=invoice_id)


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: uuid.UUID, svc: FinanceService = Depends(_svc)):
    return await svc.get_payment(payment_id)
