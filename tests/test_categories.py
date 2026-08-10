from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def test_duplicate_name_is_409():
    client.post("/v1/categories", json={"name": "Work"})
    dup = client.post("/v1/categories", json={"name": "Work"})
    assert dup.status_code == 409


def test_delete_category_sets_todo_category_null():
    cat = client.post("/v1/categories", json={"name": "Errands"}).json()
    todo = client.post(
        "/v1/todos", json={"title": "buy milk", "category_id": cat["id"]}
    ).json()
    assert client.delete(f"/v1/categories/{cat['id']}").status_code == 204
    refetched = client.get(f"/v1/todos/{todo['id']}").json()
    assert refetched["category_id"] is None  # SET NULL, not cascade delete
