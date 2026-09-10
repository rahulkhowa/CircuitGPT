from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    auth,
    uploads,
    users,
    circuits,
    quizzes,
    labs,
    vision,
    calculator,
    search,
    memory,
    notes,
    chat,
)

api_router = APIRouter()

# Include core subsystem endpoint modules
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(circuits.router, prefix="/circuits", tags=["circuits"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
api_router.include_router(labs.router, prefix="/labs", tags=["labs"])
api_router.include_router(vision.router, prefix="/vision", tags=["vision"])
api_router.include_router(calculator.router, prefix="/calculator", tags=["calculator"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
