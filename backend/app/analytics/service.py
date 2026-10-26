"""Analytics service — cross-module data aggregation."""
from __future__ import annotations

import uuid
from typing import Dict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.schemas import (
    CrmAnalytics,
    FinanceAnalytics,
    OverviewMetrics,
    ProjectsAnalytics,
)
from app.crm.models import Company, Contact, Deal, DealStage
from app.finance.models import Expense, Invoice, InvoiceStatus, Payment
from app.hr.models import Employee
from app.marketing.models import CampaignStatus, MarketingCampaign, MarketingLead
from app.projects.models import Project, ProjectStatus, Task, TaskStatus
from app.support.models import Ticket, TicketStatus
from app.users.models import User


class AnalyticsService:
    def __init__(self, session: AsyncSession, current_user: User) -> None:
        self.session = session
        self.org_id: uuid.UUID = current_user.organization_id  # type: ignore[assignment]

    async def get_overview(self) -> OverviewMetrics:
        # Total Revenue (sum of all recorded payments received)
        rev_res = await self.session.execute(
            select(func.coalesce(func.sum(Payment.amount), 0.0)).where(
                Payment.organization_id == self.org_id
            )
        )
        total_revenue = float(rev_res.scalar() or 0.0)

        # Expenses
        exp_res = await self.session.execute(
            select(func.coalesce(func.sum(Expense.amount), 0.0)).where(
                Expense.organization_id == self.org_id
            )
        )
        total_expenses = float(exp_res.scalar() or 0.0)

        # Active projects
        proj_res = await self.session.execute(
            select(func.count(Project.id)).where(
                Project.organization_id == self.org_id,
                Project.status == ProjectStatus.ACTIVE,
            )
        )
        active_projects = int(proj_res.scalar() or 0)

        # Open tasks
        tasks_res = await self.session.execute(
            select(func.count(Task.id)).where(
                Task.organization_id == self.org_id,
                Task.status.notin_([TaskStatus.DONE, TaskStatus.CANCELLED]),
            )
        )
        open_tasks = int(tasks_res.scalar() or 0)

        # Deals pipeline
        pipe_res = await self.session.execute(
            select(
                func.coalesce(func.sum(Deal.value), 0.0),
                func.count(Deal.id),
            ).where(
                Deal.organization_id == self.org_id,
                Deal.stage.notin_([DealStage.CLOSED_LOST, DealStage.CLOSED_WON]),
            )
        )
        pipe_row = pipe_res.first()
        pipeline_value = float(pipe_row[0] if pipe_row else 0.0)
        open_deals = int(pipe_row[1] if pipe_row else 0)

        # Total employees
        emp_res = await self.session.execute(
            select(func.count(Employee.id)).where(Employee.organization_id == self.org_id)
        )
        total_employees = int(emp_res.scalar() or 0)

        # Open support tickets
        tick_res = await self.session.execute(
            select(func.count(Ticket.id)).where(
                Ticket.organization_id == self.org_id,
                Ticket.status.in_([
                    TicketStatus.OPEN,
                    TicketStatus.IN_PROGRESS,
                    TicketStatus.WAITING_ON_CUSTOMER,
                ]),
            )
        )
        open_tickets = int(tick_res.scalar() or 0)

        # Active campaigns
        camp_res = await self.session.execute(
            select(func.count(MarketingCampaign.id)).where(
                MarketingCampaign.organization_id == self.org_id,
                MarketingCampaign.status == CampaignStatus.ACTIVE,
            )
        )
        active_campaigns = int(camp_res.scalar() or 0)

        # Total leads
        leads_res = await self.session.execute(
            select(func.count(MarketingLead.id)).where(
                MarketingLead.organization_id == self.org_id
            )
        )
        total_leads = int(leads_res.scalar() or 0)

        return OverviewMetrics(
            total_revenue=total_revenue,
            total_expenses=total_expenses,
            net_profit=total_revenue - total_expenses,
            active_projects=active_projects,
            open_tasks=open_tasks,
            pipeline_value=pipeline_value,
            open_deals_count=open_deals,
            total_employees=total_employees,
            open_tickets_count=open_tickets,
            active_campaigns_count=active_campaigns,
            total_leads_count=total_leads,
        )

    async def get_crm_analytics(self) -> CrmAnalytics:
        stages_res = await self.session.execute(
            select(Deal.stage, func.count(Deal.id))
            .where(Deal.organization_id == self.org_id)
            .group_by(Deal.stage)
        )
        deals_by_stage: Dict[str, int] = {
            str(stage.value if hasattr(stage, "value") else stage): count
            for stage, count in stages_res.all()
        }

        pipe_res = await self.session.execute(
            select(func.coalesce(func.sum(Deal.value), 0.0)).where(
                Deal.organization_id == self.org_id,
                Deal.stage.notin_([DealStage.CLOSED_LOST, DealStage.CLOSED_WON]),
            )
        )
        pipeline_val = float(pipe_res.scalar() or 0.0)

        won_res = await self.session.execute(
            select(func.coalesce(func.sum(Deal.value), 0.0)).where(
                Deal.organization_id == self.org_id,
                Deal.stage == DealStage.CLOSED_WON,
            )
        )
        won_val = float(won_res.scalar() or 0.0)

        contacts_res = await self.session.execute(
            select(func.count(Contact.id)).where(Contact.organization_id == self.org_id)
        )
        companies_res = await self.session.execute(
            select(func.count(Company.id)).where(Company.organization_id == self.org_id)
        )

        return CrmAnalytics(
            deals_by_stage=deals_by_stage,
            pipeline_value=pipeline_val,
            won_value=won_val,
            total_contacts=int(contacts_res.scalar() or 0),
            total_companies=int(companies_res.scalar() or 0),
        )

    async def get_projects_analytics(self) -> ProjectsAnalytics:
        status_res = await self.session.execute(
            select(Task.status, func.count(Task.id))
            .where(Task.organization_id == self.org_id)
            .group_by(Task.status)
        )
        tasks_by_status: Dict[str, int] = {
            str(st.value if hasattr(st, "value") else st): count
            for st, count in status_res.all()
        }

        proj_res = await self.session.execute(
            select(func.count(Project.id)).where(
                Project.organization_id == self.org_id,
                Project.status == ProjectStatus.ACTIVE,
            )
        )

        total_tasks_res = await self.session.execute(
            select(func.count(Task.id)).where(Task.organization_id == self.org_id)
        )

        return ProjectsAnalytics(
            tasks_by_status=tasks_by_status,
            active_projects_count=int(proj_res.scalar() or 0),
            total_tasks_count=int(total_tasks_res.scalar() or 0),
        )

    async def get_finance_analytics(self) -> FinanceAnalytics:
        invoiced_res = await self.session.execute(
            select(func.coalesce(func.sum(Invoice.total), 0.0)).where(
                Invoice.organization_id == self.org_id
            )
        )
        total_invoiced = float(invoiced_res.scalar() or 0.0)

        paid_res = await self.session.execute(
            select(func.coalesce(func.sum(Payment.amount), 0.0)).where(
                Payment.organization_id == self.org_id
            )
        )
        total_paid = float(paid_res.scalar() or 0.0)

        exp_res = await self.session.execute(
            select(func.coalesce(func.sum(Expense.amount), 0.0)).where(
                Expense.organization_id == self.org_id
            )
        )
        total_expenses = float(exp_res.scalar() or 0.0)

        return FinanceAnalytics(
            total_invoiced=total_invoiced,
            total_paid=total_paid,
            total_expenses=total_expenses,
            pending_receivables=max(0.0, total_invoiced - total_paid),
        )
