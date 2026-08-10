from fastapi import APIRouter

from app.api.routes import categories, comments, todos

api_router = APIRouter()
api_router.include_router(todos.router)
api_router.include_router(categories.router)
api_router.include_router(comments.router)
