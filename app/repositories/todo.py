import uuid

from sqlmodel import select

from app.models.todo import Todo
from app.repositories.base import BaseRepository


class TodoRepository(BaseRepository[Todo]):
    """All todo SQL. Methods take a user_id and ALWAYS scope by it."""

    model = Todo

    def get_owned(self, *, user_id: uuid.UUID, todo_id: uuid.UUID) -> Todo | None:
        """Fetch a todo only if it belongs to this user.

        Scoping every read by user_id is the tenant boundary — it's how we make
        sure user A can never read user B's data, even if they guess an id.
        (28-multi-tenancy.md.)
        """
        stmt = select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
        return self.session.exec(stmt).first()
