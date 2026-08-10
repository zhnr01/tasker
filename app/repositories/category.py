import uuid

from sqlmodel import select

from app.models.category import TodoCategory
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[TodoCategory]):
    model = TodoCategory

    def list_for_user(self, *, user_id: uuid.UUID) -> list[TodoCategory]:
        stmt = (
            select(TodoCategory)
            .where(TodoCategory.user_id == user_id)
            .order_by(TodoCategory.name)
        )
        return self._all(stmt)

    def get_owned(
        self, *, user_id: uuid.UUID, category_id: uuid.UUID
    ) -> TodoCategory | None:
        stmt = select(TodoCategory).where(
            TodoCategory.id == category_id, TodoCategory.user_id == user_id
        )
        return self.session.exec(stmt).first()

    def name_exists(
        self, *, user_id: uuid.UUID, name: str, exclude_id: uuid.UUID | None = None
    ) -> bool:
        """Pre-check for a friendly 409 (the unique index is the real guard)."""
        stmt = select(TodoCategory).where(
            TodoCategory.user_id == user_id, TodoCategory.name == name
        )
        if exclude_id is not None:
            stmt = stmt.where(TodoCategory.id != exclude_id)
        return self.session.exec(stmt).first() is not None
