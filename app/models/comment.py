import uuid

from sqlmodel import Field

from app.models.base import BaseModel


class Comment(BaseModel, table=True):
    """A comment on a todo (mirrors the Go comments table).

    todo_id is a CASCADE FK: delete the todo and its comments vanish with it.
    We also keep user_id so we know (and can authorize) the author.
    """

    __tablename__ = "comments"

    todo_id: uuid.UUID = Field(foreign_key="todos.id", index=True, nullable=False)
    user_id: uuid.UUID = Field(index=True, nullable=False)
    content: str = Field(min_length=1, max_length=2000, nullable=False)
