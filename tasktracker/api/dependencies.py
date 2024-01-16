from typing import AsyncIterator

from fastapi import Cookie, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from tasktracker.core import models
from tasktracker.core.auth import get_current_user
from tasktracker.core.db import async_session

auth_scheme = HTTPBearer()


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with async_session.begin() as session:
        yield session


async def get_user(
    access_token: str = Cookie(...),
    db_session: AsyncSession = Depends(get_db_session),
) -> models.User:
    return await get_current_user(db_session, access_token)
