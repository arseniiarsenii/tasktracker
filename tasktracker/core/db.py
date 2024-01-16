from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import QueuePool

from tasktracker import config

engine = create_async_engine(
    config.DB_CONN_STRING,
    echo=config.DB_ECHO,
    pool_size=config.DB_POOL_SIZE,
    max_overflow=config.DB_MAX_OVERFLOW,
    poolclass=QueuePool,
)
async_session = async_sessionmaker(engine)


class Base(DeclarativeBase):
    pass
