import uuid

from sqlmodel import Session

from app.models.schemas import TodoCreate, TodoUpdate
from app.models.todo import Todo
from app.repositories.todo import TodoRepository


class TodoService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = TodoRepository(session)

    def create(self, *, user_id: uuid.UUID, data: TodoCreate) -> Todo:
        # (Part 07 will validate category_id belongs to the user; Part 16 will
        #  invalidate the stats cache here.)
        return self.repo.create(user_id=user_id, data=data)

    def get(self, *, user_id: uuid.UUID, todo_id: uuid.UUID) -> Todo | None:
        return self.repo.get_owned(user_id=user_id, todo_id=todo_id)

    def update(
        self, *, user_id: uuid.UUID, todo_id: uuid.UUID, data: TodoUpdate
    ) -> Todo | None:
        todo = self.repo.get_owned(user_id=user_id, todo_id=todo_id)
        if todo is None:
            return None
        return self.repo.update(todo=todo, data=data)

    def delete(self, *, user_id: uuid.UUID, todo_id: uuid.UUID) -> bool:
        return self.repo.delete_owned(user_id=user_id, todo_id=todo_id)
