import uuid

from sqlmodel import Session

from app.models.todo import Todo
from app.repositories.todo import TodoRepository


class TodoService:
    """Business rules & orchestration for todos.

    The service is where policy lives: 'a missing todo is an error', 'completing a
    todo stamps completed_at', 'stats are cached'. It calls the repository for
    persistence and NEVER speaks HTTP. (08-layers.md.)
    """

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = TodoRepository(session)

    def get(self, *, user_id: uuid.UUID, todo_id: uuid.UUID) -> Todo | None:
        # Rule-free for now; Part 11 upgrades this to raise a typed NotFoundError.
        return self.repo.get_owned(user_id=user_id, todo_id=todo_id)
