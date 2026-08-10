import uuid
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.db import get_session
from app.services.category import CategoryService
from app.services.todo import TodoService

# --- Auth stand-in --------------------------------------------------------
# Until Part 17 (real JWT auth), every request acts as this demo user. Isolating
# it here means swapping in real auth later changes exactly ONE function.
DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def get_current_user_id() -> uuid.UUID:
    """Return the authenticated user's id.

    Part 17 replaces the body with 'decode & verify the JWT from the
    Authorization header'. Everything downstream already depends on this, so no
    other file changes. That's the payoff of a composition root.
    """
    return DEMO_USER_ID


# --- Service providers -----------------------------------------------------
def get_todo_service(
    session: Annotated[Session, Depends(get_session)],
) -> TodoService:
    """Build a TodoService for this request, wired to the request's session."""
    return TodoService(session)


def get_category_service(
    session: Annotated[Session, Depends(get_session)],
) -> CategoryService:
    return CategoryService(session)


# --- Reusable annotated types (clean route signatures) ---------------------
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]
SessionDep = Annotated[Session, Depends(get_session)]
TodoServiceDep = Annotated[TodoService, Depends(get_todo_service)]
CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
