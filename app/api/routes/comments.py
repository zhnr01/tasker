import uuid

from fastapi import APIRouter, HTTPException, status

from app.deps import CommentServiceDep, CurrentUserId
from app.models.schemas import CommentCreate, CommentRead, CommentUpdate

router = APIRouter(tags=["comments"])


@router.get("/todos/{todo_id}/comments", response_model=list[CommentRead])
def list_comments(
    todo_id: uuid.UUID, user_id: CurrentUserId, service: CommentServiceDep
):
    comments = service.list(user_id=user_id, todo_id=todo_id)
    if comments is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Todo not found")
    return comments


@router.post(
    "/todos/{todo_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
def add_comment(
    todo_id: uuid.UUID,
    body: CommentCreate,
    user_id: CurrentUserId,
    service: CommentServiceDep,
):
    comment = service.create(user_id=user_id, todo_id=todo_id, data=body)
    if comment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Todo not found")
    return comment


@router.patch("/comments/{comment_id}", response_model=CommentRead)
def edit_comment(
    comment_id: uuid.UUID,
    body: CommentUpdate,
    user_id: CurrentUserId,
    service: CommentServiceDep,
):
    comment = service.update(user_id=user_id, comment_id=comment_id, data=body)
    if comment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comment not found")
    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_comment(
    comment_id: uuid.UUID, user_id: CurrentUserId, service: CommentServiceDep
):
    if not service.delete(user_id=user_id, comment_id=comment_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comment not found")
