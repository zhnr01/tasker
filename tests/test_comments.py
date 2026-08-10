import uuid

from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def _todo(title="t"):
    return client.post("/v1/todos", json={"title": title}).json()


def test_comment_on_missing_todo_is_404():
    resp = client.post(
        f"/v1/todos/{uuid.uuid4()}/comments", json={"content": "hi"}
    )
    assert resp.status_code == 404


def test_add_and_list_comments():
    todo = _todo()
    client.post(f"/v1/todos/{todo['id']}/comments", json={"content": "one"})
    client.post(f"/v1/todos/{todo['id']}/comments", json={"content": "two"})
    listed = client.get(f"/v1/todos/{todo['id']}/comments").json()
    assert [c["content"] for c in listed] == ["one", "two"]  # created_at order


def test_deleting_todo_cascades_comments():
    todo = _todo()
    c = client.post(
        f"/v1/todos/{todo['id']}/comments", json={"content": "bye"}
    ).json()
    client.delete(f"/v1/todos/{todo['id']}")
    # The comment's parent is gone; editing it now 404s (row cascaded away).
    assert client.patch(
        f"/v1/comments/{c['id']}", json={"content": "x"}
    ).status_code == 404
