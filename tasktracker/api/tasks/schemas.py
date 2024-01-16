from datetime import datetime

from pydantic import BaseModel, EmailStr

from tasktracker.core.models import TaskStatus


class Task(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    created_by: str
    assigned_to: str
    title: str
    description: str
    status: TaskStatus


class CreateTaskRequest(BaseModel):
    assigned_to: EmailStr
    title: str
    description: str


class UpdateTaskRequest(BaseModel):
    assigned_to: EmailStr | None = None
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
