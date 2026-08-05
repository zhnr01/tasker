import uuid
from typing import Generic, TypeVar

from sqlmodel import Session, SQLModel

ModelT = TypeVar("ModelT", bound=SQLModel)


class BaseRepository(Generic[ModelT]):
    """Common CRUD plumbing shared by every repository.

    Holds the request-scoped Session and offers generic helpers. Concrete repos
    (TodoRepository, etc.) subclass this and add table-specific queries. No HTTP,
    no business rules — pure persistence. (08-layers.md.)
    """

    model: type[ModelT]

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, id: uuid.UUID) -> ModelT | None:
        return self.session.get(self.model, id)

    def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, entity: ModelT) -> None:
        self.session.delete(entity)
        self.session.commit()

    def _all(self, statement) -> list[ModelT]:
        return list(self.session.exec(statement).all())
