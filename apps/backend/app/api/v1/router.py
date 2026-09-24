from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    auth,
    uploads,
    chat,
    users,
    search,
    memory,
)

api_router = APIRouter()

# Core production subsystem routes
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
