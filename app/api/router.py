from fastapi import APIRouter

# Feature routers get imported and included here as we build them:
# from app.api.routes import todos, categories, comments, attachments, auth
# For now the aggregator is empty; Part 06 adds the todos router.

api_router = APIRouter()

# api_router.include_router(todos.router)   # Part 06
# api_router.include_router(categories.router)  # Part 07
# ...
