import uuid

from sqlmodel import select

from app.models.comment import Comment
from app.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    model = Comment

    def list_for_todo(self, *, todo_id: uuid.UUID) -> list[Comment]:
        stmt = (
            select(Comment)
            .where(Comment.todo_id == todo_id)
            .order_by(Comment.created_at)
        )
        return self._all(stmt)

    def get_owned(self, *, user_id: uuid.UUID, comment_id: uuid.UUID) -> Comment | None:
        stmt = select(Comment).where(
            Comment.id == comment_id, Comment.user_id == user_id
        )
        return self.session.exec(stmt).first()
