from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from tasktracker.core import controllers, models

from ..dependencies import get_db_session, get_user


async def get_task(
    task_id: int,
    user: models.User = Depends(get_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> models.Task:
    task = await controllers.get_task(db_session, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {task_id} not found")
    if task.assignee.id != user.id and task.creator.id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to access this task")
    return task
