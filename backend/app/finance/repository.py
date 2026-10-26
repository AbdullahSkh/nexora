"""Finance repository — data access layer."""
from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.finance.models import Budget, Expense, Invoice, InvoiceLineItem, Payment
from app.finance.schemas import (
    BudgetCreate, BudgetUpdate,
    ExpenseCreate, ExpenseUpdate,
    InvoiceCreate, InvoiceUpdate,
    PaymentCreate,
)


class InvoiceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, data: InvoiceCreate) -> Invoice:
        line_items_data = data.line_items
        invoice_data = data.model_dump(exclude={"line_items"})
        invoice = Invoice(**invoice_data, organization_id=org_id)
        self.session.add(invoice)
        await self.session.flush()  # get invoice.id before adding line items
        for li in line_items_data:
            self.session.add(InvoiceLineItem(**li.model_dump(), invoice_id=invoice.id))
        await self.session.commit()
        await self.session.refresh(invoice)
        return invoice

    async def get(self, invoice_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Invoice]:
        result = await self.session.execute(
            select(Invoice)
            .options(selectinload(Invoice.line_items))
            .where(Invoice.id == invoice_id, Invoice.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(self, org_id: uuid.UUID, status: Optional[str] = None) -> List[Invoice]:
        q = select(Invoice).options(selectinload(Invoice.line_items)).where(
            Invoice.organization_id == org_id
        )
        if status:
            q = q.where(Invoice.status == status)
        result = await self.session.execute(q.order_by(Invoice.issue_date.desc()))
        return list(result.scalars().all())

    async def update(self, invoice: Invoice, data: InvoiceUpdate) -> Invoice:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(invoice, field, value)
        self.session.add(invoice)
        await self.session.commit()
        await self.session.refresh(invoice)
        return invoice

    async def delete(self, invoice: Invoice) -> None:
        await self.session.delete(invoice)
        await self.session.commit()


class ExpenseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, submitted_by_id: uuid.UUID, data: ExpenseCreate) -> Expense:
        obj = Expense(**data.model_dump(), organization_id=org_id, submitted_by_id=submitted_by_id)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, expense_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Expense]:
        result = await self.session.execute(
            select(Expense).where(Expense.id == expense_id, Expense.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(self, org_id: uuid.UUID, category: Optional[str] = None) -> List[Expense]:
        q = select(Expense).where(Expense.organization_id == org_id)
        if category:
            q = q.where(Expense.category == category)
        result = await self.session.execute(q.order_by(Expense.expense_date.desc()))
        return list(result.scalars().all())

    async def update(self, expense: Expense, data: ExpenseUpdate) -> Expense:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(expense, field, value)
        self.session.add(expense)
        await self.session.commit()
        await self.session.refresh(expense)
        return expense

    async def delete(self, expense: Expense) -> None:
        await self.session.delete(expense)
        await self.session.commit()


class BudgetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, data: BudgetCreate) -> Budget:
        obj = Budget(**data.model_dump(), organization_id=org_id)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, budget_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Budget]:
        result = await self.session.execute(
            select(Budget).where(Budget.id == budget_id, Budget.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(self, org_id: uuid.UUID) -> List[Budget]:
        result = await self.session.execute(
            select(Budget).where(Budget.organization_id == org_id).order_by(Budget.period_start.desc())
        )
        return list(result.scalars().all())

    async def update(self, budget: Budget, data: BudgetUpdate) -> Budget:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(budget, field, value)
        self.session.add(budget)
        await self.session.commit()
        await self.session.refresh(budget)
        return budget

    async def delete(self, budget: Budget) -> None:
        await self.session.delete(budget)
        await self.session.commit()


class PaymentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, data: PaymentCreate) -> Payment:
        obj = Payment(**data.model_dump(), organization_id=org_id)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, payment_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Payment]:
        result = await self.session.execute(
            select(Payment).where(Payment.id == payment_id, Payment.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(self, org_id: uuid.UUID, invoice_id: Optional[uuid.UUID] = None) -> List[Payment]:
        q = select(Payment).where(Payment.organization_id == org_id)
        if invoice_id:
            q = q.where(Payment.invoice_id == invoice_id)
        result = await self.session.execute(q.order_by(Payment.payment_date.desc()))
        return list(result.scalars().all())
