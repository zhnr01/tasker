import uuid

from fastapi import APIRouter, HTTPException, status

from app.deps import CategoryServiceDep, CurrentUserId
from app.models.schemas import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category import DuplicateCategoryError

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(user_id: CurrentUserId, service: CategoryServiceDep):
    return service.list(user_id=user_id)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    body: CategoryCreate, user_id: CurrentUserId, service: CategoryServiceDep
):
    try:
        return service.create(user_id=user_id, data=body)
    except DuplicateCategoryError as err:
        # 409 Conflict: the request is valid but clashes with existing state.
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Category name already exists"
        ) from err


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: uuid.UUID,
    body: CategoryUpdate,
    user_id: CurrentUserId,
    service: CategoryServiceDep,
):
    try:
        category = service.update(user_id=user_id, category_id=category_id, data=body)
    except DuplicateCategoryError as err:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Category name already exists"
        ) from err
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: uuid.UUID, user_id: CurrentUserId, service: CategoryServiceDep
):
    if not service.delete(user_id=user_id, category_id=category_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
