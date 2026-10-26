"""Pydantic schemas for the Analytics module."""
from __future__ import annotations

from typing import Dict
from pydantic import BaseModel


class OverviewMetrics(BaseModel):
    total_revenue: float
    total_expenses: float
    net_profit: float
    active_projects: int
    open_tasks: int
    pipeline_value: float
    open_deals_count: int
    total_employees: int
    open_tickets_count: int
    active_campaigns_count: int
    total_leads_count: int


class CrmAnalytics(BaseModel):
    deals_by_stage: Dict[str, int]
    pipeline_value: float
    won_value: float
    total_contacts: int
    total_companies: int


class ProjectsAnalytics(BaseModel):
    tasks_by_status: Dict[str, int]
    active_projects_count: int
    total_tasks_count: int


class FinanceAnalytics(BaseModel):
    total_invoiced: float
    total_paid: float
    total_expenses: float
    pending_receivables: float
