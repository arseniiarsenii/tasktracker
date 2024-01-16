import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base
from .utils import utc_now


@enum.unique
class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class ChangeTrackingBase(Base):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=utc_now, nullable=True, index=True
    )


class User(ChangeTrackingBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), nullable=False, index=True, default=UserStatus.active)

    created_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        foreign_keys="[Task.created_by]",
        order_by="Task.created_at",
        lazy="selectin",
    )
    assigned_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        foreign_keys="[Task.assigned_to]",
        order_by="Task.created_at",
        lazy="selectin",
    )


@enum.unique
class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"
    rejected = "rejected"


class Task(ChangeTrackingBase):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False, index=True)
    assigned_to: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), nullable=False, default=TaskStatus.pending, index=True)

    creator: Mapped[User] = relationship(
        User,
        uselist=False,
        foreign_keys=[created_by],
        back_populates="created_tasks",
        lazy="joined",
    )
    assignee: Mapped[User] = relationship(
        User,
        uselist=False,
        foreign_keys=[assigned_to],
        back_populates="assigned_tasks",
        lazy="joined",
    )
