import uuid

from fastapi import APIRouter, HTTPException, status

from app.deps import CurrentUserId, TodoServiceDep
from app.models.schemas import TodoCreate, TodoRead, TodoReadPopulated, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(
    body: TodoCreate,
    user_id: CurrentUserId,
    service: TodoServiceDep,
) -> TodoRead:
    """Create a todo. 201 + the created resource (with server-set fields)."""
    todo = service.create(user_id=user_id, data=body)
    return TodoRead.model_validate(todo)


@router.get("/{todo_id}", response_model=TodoRead)
def get_todo(
    todo_id: uuid.UUID,
    user_id: CurrentUserId,
    service: TodoServiceDep,
) -> TodoRead:
    """Fetch one todo the caller owns, else 404."""
    todo = service.get(user_id=user_id, todo_id=todo_id)
    if todo is None:
        # The route is where a domain 'None' becomes an HTTP 404. Part 11
        # centralizes this so we won't repeat it in every handler.
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Todo not found")
    return TodoRead.model_validate(todo)


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(
    todo_id: uuid.UUID,
    body: TodoUpdate,
    user_id: CurrentUserId,
    service: TodoServiceDep,
) -> TodoRead:
    """Partially update a todo. Only fields present in the body change."""
    todo = service.update(user_id=user_id, todo_id=todo_id, data=body)
    if todo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Todo not found")
    return TodoRead.model_validate(todo)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: uuid.UUID,
    user_id: CurrentUserId,
    service: TodoServiceDep,
) -> None:
    """Delete a todo. 204 (no body) on success, 404 if it wasn't there."""
    if not service.delete(user_id=user_id, todo_id=todo_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Todo not found")
    # 204: intentionally return nothing.


@router.get("/{todo_id}/populated", response_model=TodoReadPopulated)
def get_todo_populated(
    todo_id: uuid.UUID,
    user_id: CurrentUserId,
    service: TodoServiceDep,
) -> TodoReadPopulated:
    """Fetch a todo with its category, children (subtasks), and comments."""
    data = service.get_populated(user_id=user_id, todo_id=todo_id)
    if data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Todo not found")
    return TodoReadPopulated.model_validate(data)
