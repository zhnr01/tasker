import uuid

from sqlmodel import Field

from app.models.base import BaseModel


class TodoCategory(BaseModel, table=True):
    """A per-user category (mirrors the Go todo_categories table).

    (name, user_id) is unique — a user can't have two 'Work' categories, but two
    different users each can. The unique index is added in the migration.
    """

    __tablename__ = "todo_categories"

    user_id: uuid.UUID = Field(index=True, nullable=False)
    name: str = Field(min_length=1, max_length=100, nullable=False)
    color: str | None = Field(default=None, max_length=20)
    description: str | None = Field(default=None, max_length=500)
