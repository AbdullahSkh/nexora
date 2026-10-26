"""Projects repository — data access layer."""
from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.projects.models import Project, Sprint, Task, TaskComment
from app.projects.schemas import (
    ProjectCreate, ProjectUpdate,
    SprintCreate, SprintUpdate,
    TaskCreate, TaskUpdate,
    TaskCommentCreate,
)


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, data: ProjectCreate) -> Project:
        obj = Project(**data.model_dump(), organization_id=org_id)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, project_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Project]:
        result = await self.session.execute(
            select(Project).where(Project.id == project_id, Project.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(self, org_id: uuid.UUID, status: Optional[str] = None) -> List[Project]:
        q = select(Project).where(Project.organization_id == org_id)
        if status:
            q = q.where(Project.status == status)
        result = await self.session.execute(q.order_by(Project.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, project: Project, data: ProjectUpdate) -> Project:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def delete(self, project: Project) -> None:
        await self.session.delete(project)
        await self.session.commit()


class SprintRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, data: SprintCreate) -> Sprint:
        obj = Sprint(**data.model_dump(), organization_id=org_id)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, sprint_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Sprint]:
        result = await self.session.execute(
            select(Sprint).where(Sprint.id == sprint_id, Sprint.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(self, org_id: uuid.UUID, project_id: Optional[uuid.UUID] = None) -> List[Sprint]:
        q = select(Sprint).where(Sprint.organization_id == org_id)
        if project_id:
            q = q.where(Sprint.project_id == project_id)
        result = await self.session.execute(q.order_by(Sprint.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, sprint: Sprint, data: SprintUpdate) -> Sprint:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(sprint, field, value)
        self.session.add(sprint)
        await self.session.commit()
        await self.session.refresh(sprint)
        return sprint

    async def delete(self, sprint: Sprint) -> None:
        await self.session.delete(sprint)
        await self.session.commit()


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: uuid.UUID, data: TaskCreate) -> Task:
        obj = Task(**data.model_dump(), organization_id=org_id)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, task_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Task]:
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.organization_id == org_id)
        )
        return result.scalars().first()

    async def list(
        self,
        org_id: uuid.UUID,
        project_id: Optional[uuid.UUID] = None,
        sprint_id: Optional[uuid.UUID] = None,
        assignee_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
    ) -> List[Task]:
        q = select(Task).where(Task.organization_id == org_id)
        if project_id:
            q = q.where(Task.project_id == project_id)
        if sprint_id:
            q = q.where(Task.sprint_id == sprint_id)
        if assignee_id:
            q = q.where(Task.assignee_id == assignee_id)
        if status:
            q = q.where(Task.status == status)
        result = await self.session.execute(q.order_by(Task.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, task: Task, data: TaskUpdate) -> Task:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task: Task) -> None:
        await self.session.delete(task)
        await self.session.commit()


class TaskCommentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self, org_id: uuid.UUID, task_id: uuid.UUID, author_id: uuid.UUID, data: TaskCommentCreate
    ) -> TaskComment:
        obj = TaskComment(
            organization_id=org_id,
            task_id=task_id,
            author_id=author_id,
            body=data.body,
        )
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def list(self, org_id: uuid.UUID, task_id: uuid.UUID) -> List[TaskComment]:
        result = await self.session.execute(
            select(TaskComment)
            .where(TaskComment.task_id == task_id, TaskComment.organization_id == org_id)
            .order_by(TaskComment.created_at.asc())
        )
        return list(result.scalars().all())

    async def delete(self, comment: TaskComment) -> None:
        await self.session.delete(comment)
        await self.session.commit()
