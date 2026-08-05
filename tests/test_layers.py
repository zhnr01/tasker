import uuid

from app.models.todo import Todo
from app.services.todo import TodoService


class FakeRepo:
    """A stand-in repository: returns a canned todo, records the call."""

    def __init__(self, todo: Todo | None):
        self._todo = todo
        self.called_with: dict | None = None

    def get_owned(self, *, user_id, todo_id):
        self.called_with = {"user_id": user_id, "todo_id": todo_id}
        return self._todo


def test_service_delegates_to_repo_with_scoping():
    uid = uuid.uuid4()
    tid = uuid.uuid4()
    todo = Todo(id=tid, user_id=uid, title="x")

    # Build the service WITHOUT a session, then inject the fake repo.
    svc = TodoService.__new__(TodoService)  # skip __init__ (needs a Session)
    svc.repo = FakeRepo(todo)

    result = svc.get(user_id=uid, todo_id=tid)

    assert result is todo
    # The service must scope by user_id — verify it passed it through.
    assert svc.repo.called_with == {"user_id": uid, "todo_id": tid}
