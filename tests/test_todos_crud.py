from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())
BASE = "/v1/todos"


def _create(title="task", **extra):
    return client.post(BASE, json={"title": title, **extra}).json()


def test_create_defaults_to_draft_v1():
    todo = _create("first")
    assert todo["status"] == "draft"  # Go-parity default
    assert todo["priority"] == "medium"
    assert todo["version"] == 1
    assert todo["completed_at"] is None


def test_partial_update_leaves_other_fields():
    todo = _create("keep me", description="original")
    resp = client.patch(f"{BASE}/{todo['id']}", json={"title": "renamed"})
    body = resp.json()
    assert resp.status_code == 200
    assert body["title"] == "renamed"
    assert body["description"] == "original"


def test_completing_sets_completed_at_and_reopening_clears_it():
    todo = _create("finish me")
    done = client.patch(f"{BASE}/{todo['id']}", json={"status": "completed"}).json()
    assert done["completed_at"] is not None
    reopened = client.patch(f"{BASE}/{todo['id']}", json={"status": "active"}).json()
    assert reopened["completed_at"] is None


def test_get_missing_is_404():
    import uuid

    assert client.get(f"{BASE}/{uuid.uuid4()}").status_code == 404


def test_delete_then_get_is_404():
    todo = _create("temp")
    assert client.delete(f"{BASE}/{todo['id']}").status_code == 204
    assert client.get(f"{BASE}/{todo['id']}").status_code == 404
