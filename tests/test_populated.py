from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def _todo(title, **extra):
    return client.post("/v1/todos", json={"title": title, **extra}).json()


def test_populated_returns_children_and_comments():
    parent = _todo("parent")
    _todo("child A", parent_todo_id=parent["id"])
    _todo("child B", parent_todo_id=parent["id"])
    client.post(f"/v1/todos/{parent['id']}/comments", json={"content": "hi"})

    data = client.get(f"/v1/todos/{parent['id']}/populated").json()

    assert {c["title"] for c in data["children"]} == {"child A", "child B"}
    assert [c["content"] for c in data["comments"]] == ["hi"]
    assert data["category"] is None
