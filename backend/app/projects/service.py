"""Projects service — business logic."""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.projects.models import Project, Sprint, Task, TaskComment
from app.projects.repository import (
    ProjectRepository, SprintRepository,
    TaskRepository, TaskCommentRepository,
)
from app.projects.schemas import (
    ProjectCreate, ProjectUpdate,
    SprintCreate, SprintUpdate,
    TaskCreate, TaskUpdate,
    TaskCommentCreate,
)
from app.users.models import User


def _not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


class ProjectService:
    def __init__(self, session: AsyncSession, current_user: User) -> None:
        self.org_id: uuid.UUID = current_user.organization_id  # type: ignore[assignment]
        self.user_id: uuid.UUID = current_user.id
        self.project_repo = ProjectRepository(session)
        self.sprint_repo = SprintRepository(session)
        self.task_repo = TaskRepository(session)
        self.comment_repo = TaskCommentRepository(session)

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    async def create_project(self, data: ProjectCreate) -> Project:
        return await self.project_repo.create(self.org_id, data)

    async def get_project(self, project_id: uuid.UUID) -> Project:
        obj = await self.project_repo.get(project_id, self.org_id)
        if not obj:
            raise _not_found("Project")
        return obj

    async def list_projects(self, status: Optional[str] = None) -> List[Project]:
        return await self.project_repo.list(self.org_id, status=status)

    async def update_project(self, project_id: uuid.UUID, data: ProjectUpdate) -> Project:
        obj = await self.get_project(project_id)
        return await self.project_repo.update(obj, data)

    async def delete_project(self, project_id: uuid.UUID) -> None:
        obj = await self.get_project(project_id)
        await self.project_repo.delete(obj)

    # ------------------------------------------------------------------
    # Sprints
    # ------------------------------------------------------------------

    async def create_sprint(self, data: SprintCreate) -> Sprint:
        # Verify the project belongs to the org
        await self.get_project(data.project_id)
        return await self.sprint_repo.create(self.org_id, data)

    async def get_sprint(self, sprint_id: uuid.UUID) -> Sprint:
        obj = await self.sprint_repo.get(sprint_id, self.org_id)
        if not obj:
            raise _not_found("Sprint")
        return obj

    async def list_sprints(self, project_id: Optional[uuid.UUID] = None) -> List[Sprint]:
        return await self.sprint_repo.list(self.org_id, project_id=project_id)

    async def update_sprint(self, sprint_id: uuid.UUID, data: SprintUpdate) -> Sprint:
        obj = await self.get_sprint(sprint_id)
        return await self.sprint_repo.update(obj, data)

    async def delete_sprint(self, sprint_id: uuid.UUID) -> None:
        obj = await self.get_sprint(sprint_id)
        await self.sprint_repo.delete(obj)

    # ------------------------------------------------------------------
    # Tasks
    # ------------------------------------------------------------------

    async def create_task(self, data: TaskCreate) -> Task:
        await self.get_project(data.project_id)
        return await self.task_repo.create(self.org_id, data)

    async def get_task(self, task_id: uuid.UUID) -> Task:
        obj = await self.task_repo.get(task_id, self.org_id)
        if not obj:
            raise _not_found("Task")
        return obj

    async def list_tasks(
        self,
        project_id: Optional[uuid.UUID] = None,
        sprint_id: Optional[uuid.UUID] = None,
        assignee_id: Optional[uuid.UUID] = None,
        task_status: Optional[str] = None,
    ) -> List[Task]:
        return await self.task_repo.list(
            self.org_id,
            project_id=project_id,
            sprint_id=sprint_id,
            assignee_id=assignee_id,
            status=task_status,
        )

    async def update_task(self, task_id: uuid.UUID, data: TaskUpdate) -> Task:
        obj = await self.get_task(task_id)
        return await self.task_repo.update(obj, data)

    async def delete_task(self, task_id: uuid.UUID) -> None:
        obj = await self.get_task(task_id)
        await self.task_repo.delete(obj)

    # ------------------------------------------------------------------
    # Comments
    # ------------------------------------------------------------------

    async def add_comment(self, task_id: uuid.UUID, data: TaskCommentCreate) -> TaskComment:
        await self.get_task(task_id)
        return await self.comment_repo.create(self.org_id, task_id, self.user_id, data)

    async def list_comments(self, task_id: uuid.UUID) -> List[TaskComment]:
        await self.get_task(task_id)
        return await self.comment_repo.list(self.org_id, task_id)
