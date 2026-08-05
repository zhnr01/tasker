import uuid
from datetime import datetime

from pydantic import BaseModel as PydanticBase
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.base import BaseModel
from app.models.enums import TodoPriority, TodoStatus


class TodoMetadata(PydanticBase):
    """Free-form-ish metadata stored as JSONB (mirrors Go's todo.Metadata).

    Kept as a typed object (not a raw dict) so we validate its shape while still
    enjoying JSONB flexibility in the database.
    """

    tags: list[str] = []
    reminder: str | None = None
    color: str | None = None
    difficulty: int | None = None


class Todo(BaseModel, table=True):
    """A todo row. Inherits id/created_at/updated_at from BaseModel.

    Everything here maps 1:1 to the Go `todos` table, plus a `version` column we
    add for optimistic concurrency (Part 13) — the Go app's main gap.
    """

    __tablename__ = "todos"

    # Ownership: which user this belongs to. Indexed because every query filters
    # by it (and it's the tenant boundary — see 28-multi-tenancy.md).
    user_id: uuid.UUID = Field(index=True, nullable=False)

    # Core content.
    title: str = Field(min_length=1, max_length=255, nullable=False)
    description: str | None = Field(default=None, max_length=4000)

    # Lifecycle & priority (defaults match the Go app: draft + medium).
    status: TodoStatus = Field(default=TodoStatus.DRAFT, index=True, nullable=False)
    priority: TodoPriority = Field(
        default=TodoPriority.MEDIUM, index=True, nullable=False
    )

    # Scheduling.
    due_date: datetime | None = Field(default=None, index=True)
    completed_at: datetime | None = Field(default=None)

    # Relations (FKs added in the migration; see §4.7).
    parent_todo_id: uuid.UUID | None = Field(
        default=None, foreign_key="todos.id", index=True
    )
    category_id: uuid.UUID | None = Field(
        default=None, foreign_key="todo_categories.id", index=True
    )

    # JSONB metadata — stored as a dict; validated via TodoMetadata at the edges.
    metadata_: dict | None = Field(
        default=None,
        sa_column=Column("metadata", JSONB, nullable=True),
    )

    # Ordering within a parent (the Go app uses a SERIAL sort_order).
    sort_order: int = Field(default=0, index=True)

    # Optimistic-lock version. Every successful update bumps this (Part 13).
    version: int = Field(default=1, nullable=False)
