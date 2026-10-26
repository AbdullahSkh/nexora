"""Pydantic schemas for the Projects module."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.projects.models import ProjectStatus, TaskPriority, TaskStatus


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    owner_id: Optional[uuid.UUID] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    owner_id: Optional[uuid.UUID] = None


class ProjectResponse(ProjectBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Sprint
# ---------------------------------------------------------------------------


class SprintBase(BaseModel):
    name: str
    goal: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_active: bool = False


class SprintCreate(SprintBase):
    project_id: uuid.UUID


class SprintUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_active: Optional[bool] = None


class SprintResponse(SprintBase):
    id: uuid.UUID
    project_id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.BACKLOG
    priority: TaskPriority = TaskPriority.MEDIUM
    story_points: Optional[int] = None
    due_date: Optional[str] = None
    assignee_id: Optional[uuid.UUID] = None
    sprint_id: Optional[uuid.UUID] = None
    parent_task_id: Optional[uuid.UUID] = None


class TaskCreate(TaskBase):
    project_id: uuid.UUID
    reporter_id: Optional[uuid.UUID] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    story_points: Optional[int] = None
    due_date: Optional[str] = None
    assignee_id: Optional[uuid.UUID] = None
    sprint_id: Optional[uuid.UUID] = None


class TaskResponse(TaskBase):
    id: uuid.UUID
    project_id: uuid.UUID
    organization_id: uuid.UUID
    reporter_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Task Comment
# ---------------------------------------------------------------------------


class TaskCommentCreate(BaseModel):
    body: str


class TaskCommentResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    organization_id: uuid.UUID
    author_id: Optional[uuid.UUID] = None
    body: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
