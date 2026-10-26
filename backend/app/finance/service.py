"""Finance service — business logic."""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.models import Budget, Expense, Invoice, Payment
from app.finance.repository import (
    BudgetRepository, ExpenseRepository, InvoiceRepository, PaymentRepository
)
from app.finance.schemas import (
    BudgetCreate, BudgetUpdate,
    ExpenseCreate, ExpenseUpdate,
    InvoiceCreate, InvoiceUpdate,
    PaymentCreate,
)
from app.users.models import User


def _not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


class FinanceService:
    def __init__(self, session: AsyncSession, current_user: User) -> None:
        self.org_id: uuid.UUID = current_user.organization_id  # type: ignore[assignment]
        self.user_id: uuid.UUID = current_user.id
        self.is_admin: bool = current_user.is_superuser
        self.invoice_repo = InvoiceRepository(session)
        self.expense_repo = ExpenseRepository(session)
        self.budget_repo = BudgetRepository(session)
        self.payment_repo = PaymentRepository(session)

    def _require_admin(self) -> None:
        if not self.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    # ------------------------------------------------------------------
    # Invoices
    # ------------------------------------------------------------------

    async def create_invoice(self, data: InvoiceCreate) -> Invoice:
        self._require_admin()
        return await self.invoice_repo.create(self.org_id, data)

    async def get_invoice(self, invoice_id: uuid.UUID) -> Invoice:
        obj = await self.invoice_repo.get(invoice_id, self.org_id)
        if not obj:
            raise _not_found("Invoice")
        return obj

    async def list_invoices(self, status: Optional[str] = None) -> List[Invoice]:
        return await self.invoice_repo.list(self.org_id, status=status)

    async def update_invoice(self, invoice_id: uuid.UUID, data: InvoiceUpdate) -> Invoice:
        self._require_admin()
        obj = await self.get_invoice(invoice_id)
        return await self.invoice_repo.update(obj, data)

    async def delete_invoice(self, invoice_id: uuid.UUID) -> None:
        self._require_admin()
        obj = await self.get_invoice(invoice_id)
        await self.invoice_repo.delete(obj)

    # ------------------------------------------------------------------
    # Expenses
    # ------------------------------------------------------------------

    async def create_expense(self, data: ExpenseCreate) -> Expense:
        return await self.expense_repo.create(self.org_id, self.user_id, data)

    async def get_expense(self, expense_id: uuid.UUID) -> Expense:
        obj = await self.expense_repo.get(expense_id, self.org_id)
        if not obj:
            raise _not_found("Expense")
        return obj

    async def list_expenses(self, category: Optional[str] = None) -> List[Expense]:
        return await self.expense_repo.list(self.org_id, category=category)

    async def update_expense(self, expense_id: uuid.UUID, data: ExpenseUpdate) -> Expense:
        obj = await self.get_expense(expense_id)
        return await self.expense_repo.update(obj, data)

    async def delete_expense(self, expense_id: uuid.UUID) -> None:
        obj = await self.get_expense(expense_id)
        await self.expense_repo.delete(obj)

    # ------------------------------------------------------------------
    # Budgets
    # ------------------------------------------------------------------

    async def create_budget(self, data: BudgetCreate) -> Budget:
        self._require_admin()
        return await self.budget_repo.create(self.org_id, data)

    async def get_budget(self, budget_id: uuid.UUID) -> Budget:
        obj = await self.budget_repo.get(budget_id, self.org_id)
        if not obj:
            raise _not_found("Budget")
        return obj

    async def list_budgets(self) -> List[Budget]:
        return await self.budget_repo.list(self.org_id)

    async def update_budget(self, budget_id: uuid.UUID, data: BudgetUpdate) -> Budget:
        self._require_admin()
        obj = await self.get_budget(budget_id)
        return await self.budget_repo.update(obj, data)

    async def delete_budget(self, budget_id: uuid.UUID) -> None:
        self._require_admin()
        obj = await self.get_budget(budget_id)
        await self.budget_repo.delete(obj)

    # ------------------------------------------------------------------
    # Payments
    # ------------------------------------------------------------------

    async def create_payment(self, data: PaymentCreate) -> Payment:
        self._require_admin()
        return await self.payment_repo.create(self.org_id, data)

    async def get_payment(self, payment_id: uuid.UUID) -> Payment:
        obj = await self.payment_repo.get(payment_id, self.org_id)
        if not obj:
            raise _not_found("Payment")
        return obj

    async def list_payments(self, invoice_id: Optional[uuid.UUID] = None) -> List[Payment]:
        return await self.payment_repo.list(self.org_id, invoice_id=invoice_id)
