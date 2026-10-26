"""Projects API router."""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.projects.schemas import (
    ProjectCreate, ProjectResponse, ProjectUpdate,
    SprintCreate, SprintResponse, SprintUpdate,
    TaskCommentCreate, TaskCommentResponse,
    TaskCreate, TaskResponse, TaskUpdate,
)
from app.projects.service import ProjectService
from app.users.models import User

router = APIRouter()


def _svc(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectService:
    return ProjectService(db, current_user)


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(data: ProjectCreate, svc: ProjectService = Depends(_svc)):
    return await svc.create_project(data)


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    project_status: Optional[str] = Query(None, alias="status"),
    svc: ProjectService = Depends(_svc),
):
    return await svc.list_projects(status=project_status)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: uuid.UUID, svc: ProjectService = Depends(_svc)):
    return await svc.get_project(project_id)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: uuid.UUID, data: ProjectUpdate, svc: ProjectService = Depends(_svc)):
    return await svc.update_project(project_id, data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: uuid.UUID, svc: ProjectService = Depends(_svc)):
    await svc.delete_project(project_id)


# ---------------------------------------------------------------------------
# Sprints
# ---------------------------------------------------------------------------


@router.post("/sprints", response_model=SprintResponse, status_code=status.HTTP_201_CREATED)
async def create_sprint(data: SprintCreate, svc: ProjectService = Depends(_svc)):
    return await svc.create_sprint(data)


@router.get("/sprints", response_model=List[SprintResponse])
async def list_sprints(
    project_id: Optional[uuid.UUID] = Query(None),
    svc: ProjectService = Depends(_svc),
):
    return await svc.list_sprints(project_id=project_id)


@router.get("/sprints/{sprint_id}", response_model=SprintResponse)
async def get_sprint(sprint_id: uuid.UUID, svc: ProjectService = Depends(_svc)):
    return await svc.get_sprint(sprint_id)


@router.patch("/sprints/{sprint_id}", response_model=SprintResponse)
async def update_sprint(sprint_id: uuid.UUID, data: SprintUpdate, svc: ProjectService = Depends(_svc)):
    return await svc.update_sprint(sprint_id, data)


@router.delete("/sprints/{sprint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sprint(sprint_id: uuid.UUID, svc: ProjectService = Depends(_svc)):
    await svc.delete_sprint(sprint_id)


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(data: TaskCreate, svc: ProjectService = Depends(_svc)):
    return await svc.create_task(data)


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    project_id: Optional[uuid.UUID] = Query(None),
    sprint_id: Optional[uuid.UUID] = Query(None),
    assignee_id: Optional[uuid.UUID] = Query(None),
    task_status: Optional[str] = Query(None, alias="status"),
    svc: ProjectService = Depends(_svc),
):
    return await svc.list_tasks(
        project_id=project_id,
        sprint_id=sprint_id,
        assignee_id=assignee_id,
        task_status=task_status,
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: uuid.UUID, svc: ProjectService = Depends(_svc)):
    return await svc.get_task(task_id)


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: uuid.UUID, data: TaskUpdate, svc: ProjectService = Depends(_svc)):
    return await svc.update_task(task_id, data)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: uuid.UUID, svc: ProjectService = Depends(_svc)):
    await svc.delete_task(task_id)


# ---------------------------------------------------------------------------
# Task Comments
# ---------------------------------------------------------------------------


@router.post("/tasks/{task_id}/comments", response_model=TaskCommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(task_id: uuid.UUID, data: TaskCommentCreate, svc: ProjectService = Depends(_svc)):
    return await svc.add_comment(task_id, data)


@router.get("/tasks/{task_id}/comments", response_model=List[TaskCommentResponse])
async def list_comments(task_id: uuid.UUID, svc: ProjectService = Depends(_svc)):
    return await svc.list_comments(task_id)
