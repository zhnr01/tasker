from sqlmodel import Session

from app.models.comment import Comment
from app.models.schemas import CommentCreate, CommentUpdate
from app.repositories.comment import CommentRepository
from app.repositories.todo import TodoRepository


class CommentService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = CommentRepository(session)
        self.todos = TodoRepository(session)  # to verify parent ownership

    def _own_todo_or_none(self, *, user_id, todo_id):
        return self.todos.get_owned(user_id=user_id, todo_id=todo_id)

    def list(self, *, user_id, todo_id) -> list[Comment] | None:
        if self._own_todo_or_none(user_id=user_id, todo_id=todo_id) is None:
            return None  # route turns this into 404 for the todo
        return self.repo.list_for_todo(todo_id=todo_id)

    def create(self, *, user_id, todo_id, data: CommentCreate) -> Comment | None:
        if self._own_todo_or_none(user_id=user_id, todo_id=todo_id) is None:
            return None
        comment = Comment(todo_id=todo_id, user_id=user_id, content=data.content)
        return self.repo.add(comment)

    def update(self, *, user_id, comment_id, data: CommentUpdate) -> Comment | None:
        comment = self.repo.get_owned(user_id=user_id, comment_id=comment_id)
        if comment is None:
            return None
        comment.content = data.content
        return self.repo.add(comment)

    def delete(self, *, user_id, comment_id) -> bool:
        comment = self.repo.get_owned(user_id=user_id, comment_id=comment_id)
        if comment is None:
            return False
        self.repo.delete(comment)
        return True
