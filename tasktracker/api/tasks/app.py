from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from tasktracker.core import controllers, models

from .. import templates
from ..dependencies import get_db_session, get_user
from . import schemas
from .dependencies import get_task

router = APIRouter(tags=["Tasks"])


def _convert_task_model_to_schema(task: models.Task) -> schemas.Task:
    return schemas.Task(
        id=task.id,
        created_at=task.created_at,
        updated_at=task.updated_at,
        created_by=task.creator.name,
        assigned_to=task.assignee.name,
        title=task.title,
        description=task.description,
        status=task.status,
    )


@router.get("/my-tasks")
async def get_my_tasks(request: Request, current_user: models.User = Depends(get_user)) -> HTMLResponse:
    assigned_tasks = [_convert_task_model_to_schema(task) for task in current_user.assigned_tasks]
    created_tasks = [_convert_task_model_to_schema(task) for task in current_user.created_tasks]
    return templates.TemplateResponse(
        "mytasks.html",
        {
            "request": request,
            "assigned_tasks": assigned_tasks,
            "created_tasks": created_tasks,
            "current_user": current_user,
        },
    )


@router.get("/new-task")
async def make_new_task(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "newtask.html",
        {"request": request},
    )


@router.post("/create-task")
async def create_task(
    task_details: schemas.CreateTaskRequest,
    creator: models.User = Depends(get_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> schemas.Task:
    assignee = await controllers.get_user_by_email(db_session, task_details.assigned_to)
    if assignee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email {task_details.assigned_to} not found"
        )
    task = await controllers.create_task(db_session, creator, assignee, task_details.title, task_details.description)
    await db_session.flush()
    await db_session.refresh(task)
    return _convert_task_model_to_schema(task)


@router.get("/{task_id}")
async def get_task_details(task: models.Task = Depends(get_task)) -> schemas.Task:
    return _convert_task_model_to_schema(task)


@router.get("/view/{task_id}")
async def view_task_details(request: Request, task: models.Task = Depends(get_task)) -> HTMLResponse:
    task_schema = _convert_task_model_to_schema(task)
    task_schema.assigned_to = task.assignee.email
    return templates.TemplateResponse(
        "viewtask.html",
        {"request": request, "task": task_schema},
    )


@router.patch("/{task_id}")
async def update_task(
    task_details: schemas.UpdateTaskRequest,
    task: models.Task = Depends(get_task),
    db_session: AsyncSession = Depends(get_db_session),
) -> schemas.Task:
    if task_details.assigned_to is not None:
        assignee = await controllers.get_user_by_email(db_session, task_details.assigned_to)
        if assignee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {task_details.assigned_to} not found",
            )
        task.assigned_to = assignee.id
    if task_details.title is not None:
        task.title = task_details.title
    if task_details.description is not None:
        task.description = task_details.description
    if task_details.status is not None:
        task.status = task_details.status
    await db_session.flush()
    await db_session.refresh(task)
    return _convert_task_model_to_schema(task)


@router.delete("/{task_id}")
async def delete_task(
    task: models.Task = Depends(get_task),
    requester: models.User = Depends(get_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> None:
    await controllers.delete_task(db_session, requester, task)


@router.get("/list/created-by-me")
async def get_tasks_created_by_me(creator: models.User = Depends(get_user)) -> list[schemas.Task]:
    return [_convert_task_model_to_schema(task) for task in creator.created_tasks]


@router.get("/list/assigned-to-me")
async def get_tasks_assigned_to_me(assignee: models.User = Depends(get_user)) -> list[schemas.Task]:
    return [_convert_task_model_to_schema(task) for task in assignee.assigned_tasks]
