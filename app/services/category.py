import uuid

from sqlmodel import Session

from app.models.category import TodoCategory
from app.models.schemas import CategoryCreate, CategoryUpdate
from app.repositories.category import CategoryRepository


class DuplicateCategoryError(Exception):
    """Raised when a user already has a category with the same name.

    A plain domain exception for now; Part 11 folds it into the typed error
    hierarchy that maps to HTTP 409.
    """


class CategoryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = CategoryRepository(session)

    def list(self, *, user_id: uuid.UUID) -> list[TodoCategory]:
        return self.repo.list_for_user(user_id=user_id)

    def get(self, *, user_id, category_id) -> TodoCategory | None:
        return self.repo.get_owned(user_id=user_id, category_id=category_id)

    def create(self, *, user_id: uuid.UUID, data: CategoryCreate) -> TodoCategory:
        if self.repo.name_exists(user_id=user_id, name=data.name):
            raise DuplicateCategoryError(data.name)
        category = TodoCategory(user_id=user_id, **data.model_dump())
        return self.repo.add(category)

    def update(
        self, *, user_id, category_id, data: CategoryUpdate
    ) -> TodoCategory | None:
        category = self.repo.get_owned(user_id=user_id, category_id=category_id)
        if category is None:
            return None
        patch = data.model_dump(exclude_unset=True)
        if "name" in patch and self.repo.name_exists(
            user_id=user_id, name=patch["name"], exclude_id=category_id
        ):
            raise DuplicateCategoryError(patch["name"])
        for k, v in patch.items():
            setattr(category, k, v)
        return self.repo.add(category)

    def delete(self, *, user_id, category_id) -> bool:
        category = self.repo.get_owned(user_id=user_id, category_id=category_id)
        if category is None:
            return False
        # ON DELETE SET NULL (schema) auto-unlinks todos — we don't touch them.
        self.repo.delete(category)
        return True
