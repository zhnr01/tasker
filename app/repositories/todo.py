import uuid

from sqlmodel import select

from app.models.base import utcnow
from app.models.category import TodoCategory
from app.models.comment import Comment
from app.models.enums import TodoStatus
from app.models.schemas import TodoCreate, TodoUpdate
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

    def create(self, *, user_id: uuid.UUID, data: TodoCreate) -> Todo:
        """Insert a new todo owned by user_id.

        The client-supplied fields come from TodoCreate; the server owns
        user_id, id, status(default draft), timestamps, and version.
        """
        todo = Todo(
            user_id=user_id,
            title=data.title,
            description=data.description,
            priority=data.priority or Todo.model_fields["priority"].default,
            due_date=data.due_date,
            parent_todo_id=data.parent_todo_id,
            category_id=data.category_id,
            metadata_=data.metadata.model_dump() if data.metadata else None,
        )
        return self.add(todo)  # add() commits + refreshes (BaseRepository)

    def update(self, *, todo: Todo, data: TodoUpdate) -> Todo:
        """Apply a partial update to an already-fetched, owned todo.

        Only fields the client actually SENT are changed (exclude_unset). This is
        the heart of PATCH: omitting a field means 'leave it', not 'null it'.
        """
        patch = data.model_dump(exclude_unset=True)

        # Special-case metadata: it's a nested model → dump to a plain dict.
        if "metadata" in patch and data.metadata is not None:
            patch["metadata_"] = data.metadata.model_dump()
            patch.pop("metadata")
        elif "metadata" in patch:  # explicitly set to null → clear it
            patch["metadata_"] = None
            patch.pop("metadata")

        # Business rule from the Go app: keep completed_at in sync with status.
        if "status" in patch:
            if patch["status"] == TodoStatus.COMPLETED:
                todo.completed_at = utcnow()
            else:
                todo.completed_at = None

        for key, value in patch.items():
            setattr(todo, key, value)

        todo.updated_at = utcnow()
        return self.add(todo)

    def delete_owned(self, *, user_id: uuid.UUID, todo_id: uuid.UUID) -> bool:
        """Hard-delete a todo if it belongs to the user. Returns False if absent.

        The Go app hard-deletes (DELETE ... WHERE id AND user_id) and relies on
        ON DELETE CASCADE to remove child comments/attachments. We match that.
        """
        todo = self.get_owned(user_id=user_id, todo_id=todo_id)
        if todo is None:
            return False
        self.delete(todo)  # BaseRepository.delete commits
        return True

    def get_populated(self, *, user_id: uuid.UUID, todo_id: uuid.UUID) -> dict | None:
        """Fetch one todo plus its category, children, and comments.

        Returns a plain dict shaped for TodoReadPopulated, or None if the todo
        isn't found / not owned. We use a few batched queries (not 1-per-child)
        so this stays O(1) round-trips regardless of how many children exist.
        """
        todo = self.get_owned(user_id=user_id, todo_id=todo_id)
        if todo is None:
            return None

        # 1) category (one row, by FK) — only if set.
        category = None
        if todo.category_id is not None:
            category = self.session.get(TodoCategory, todo.category_id)

        # 2) children (subtasks), ordered like the Go app: by sort_order.
        children_stmt = (
            select(Todo)
            .where(Todo.parent_todo_id == todo_id, Todo.user_id == user_id)
            .order_by(Todo.sort_order, Todo.created_at)
        )
        children = self._all(children_stmt)

        # 3) comments, oldest first.
        comments_stmt = (
            select(Comment)
            .where(Comment.todo_id == todo_id)
            .order_by(Comment.created_at)
        )
        comments = self._all(comments_stmt)

        # Assemble the dict the populated schema expects. metadata_ → metadata
        # is handled by the schema alias when we validate.
        data = todo.model_dump()
        data["category"] = category.model_dump() if category else None
        data["children"] = [c.model_dump() for c in children]
        data["comments"] = [c.model_dump() for c in comments]
        return data

    def children_for_parents(
        self, *, user_id: uuid.UUID, parent_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, list[Todo]]:
        """Batch-load children for many parents in ONE query (kills N+1).

        Returns {parent_id: [child, ...]}. Part 10's list endpoint uses this to
        attach children to a page of todos without a per-row query.
        """
        if not parent_ids:
            return {}
        stmt = (
            select(Todo)
            .where(Todo.parent_todo_id.in_(parent_ids), Todo.user_id == user_id)
            .order_by(Todo.sort_order, Todo.created_at)
        )
        grouped: dict[uuid.UUID, list[Todo]] = {pid: [] for pid in parent_ids}
        for child in self._all(stmt):
            grouped[child.parent_todo_id].append(child)
        return grouped
