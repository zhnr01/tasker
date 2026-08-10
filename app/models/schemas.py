import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TodoPriority, TodoStatus
from app.models.todo import TodoMetadata


class TodoCreate(BaseModel):
    """Body for POST /todos. Only fields a client may set at creation.

    Mirrors Go's CreateTodoPayload: title required; the rest optional. Note the
    client cannot set status (new todos start 'draft') or user_id (the server
    stamps it from the authenticated identity).
    """

    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    priority: TodoPriority | None = None
    due_date: datetime | None = None
    parent_todo_id: uuid.UUID | None = None
    category_id: uuid.UUID | None = None
    metadata: TodoMetadata | None = None


class TodoUpdate(BaseModel):
    """Body for PATCH /todos/{id}. EVERY field optional (partial update).

    Mirrors Go's UpdateTodoPayload. Presence matters: a field left out means
    'leave unchanged'; a field set to null means 'clear it'. We honor that in the
    repository via exclude_unset (Part 06).
    """

    model_config = ConfigDict(extra="forbid")  # reject unknown keys loudly

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    status: TodoStatus | None = None
    priority: TodoPriority | None = None
    due_date: datetime | None = None
    parent_todo_id: uuid.UUID | None = None
    category_id: uuid.UUID | None = None
    metadata: TodoMetadata | None = None


class TodoRead(BaseModel):
    """Response body for a single todo (the non-populated shape).

    from_attributes=True lets us build this straight from a Todo ORM object.
    The alias maps the DB attribute metadata_ back to the wire name 'metadata'.
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str | None
    status: TodoStatus
    priority: TodoPriority
    due_date: datetime | None
    completed_at: datetime | None
    parent_todo_id: uuid.UUID | None
    category_id: uuid.UUID | None
    metadata: TodoMetadata | None = Field(default=None, alias="metadata_")
    sort_order: int
    version: int
    created_at: datetime
    updated_at: datetime


class TodoStats(BaseModel):
    """Aggregate counts (mirrors Go's todo.TodoStats). Populated in Part 10/16."""

    total: int = 0
    draft: int = 0
    active: int = 0
    completed: int = 0
    archived: int = 0
    overdue: int = 0


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    color: str | None = Field(default=None, max_length=20)
    description: str | None = Field(default=None, max_length=500)


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = Field(default=None, max_length=20)
    description: str | None = Field(default=None, max_length=500)


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    color: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CommentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content: str = Field(min_length=1, max_length=2000)


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    todo_id: uuid.UUID
    user_id: uuid.UUID
    content: str
    created_at: datetime
    updated_at: datetime


class TodoReadPopulated(TodoRead):
    """A todo with its relations embedded (mirrors the Go populated todo).

    Inherits every base field from TodoRead and adds the nested collections.
    'children' are subtasks (todos whose parent_todo_id == this id).
    """

    category: "CategoryRead | None" = None
    children: list["TodoRead"] = []
    comments: list["CommentRead"] = []
    # attachments: list[AttachmentRead] = []   # wired in Part 20


# Pydantic needs the forward refs resolved once all classes are defined:
TodoReadPopulated.model_rebuild()
