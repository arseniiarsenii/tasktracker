from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models


async def create_user(db_session: AsyncSession, email: str, password: str, name: str) -> models.User:
    from .auth import hash_password

    user = models.User(
        email=email,
        hashed_password=hash_password(password),
        name=name,
    )
    db_session.add(user)
    return user


async def get_user_by_email(db_session: AsyncSession, email: str) -> models.User | None:
    return (await db_session.execute(select(models.User).where(models.User.email == email))).scalar_one_or_none()


async def create_task(
    db_session: AsyncSession,
    creator: models.User,
    assignee: models.User,
    title: str,
    description: str,
) -> models.Task:
    task = models.Task(
        created_by=creator.id,
        assigned_to=assignee.id,
        title=title,
        description=description,
    )
    db_session.add(task)
    return task


async def get_task(db_session: AsyncSession, task_id: int) -> models.Task | None:
    return (await db_session.execute(select(models.Task).where(models.Task.id == task_id))).scalar_one_or_none()


async def delete_task(db_session: AsyncSession, requester: models.User, task: models.Task) -> None:
    if requester.id != task.created_by:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete tasks created by you",
        )
    await db_session.delete(task)
