# Import all models here so Alembic can auto-detect them during migration generation.
# The order of imports matters for foreign key dependencies.

from app.models.base import Base, BaseModel
from app.models.role import UserRole
from app.models.user import User
from app.models.course import Course
from app.models.module import Module
from app.models.note import Note, NoteStatus
from app.models.note_evaluation import NoteEvaluation
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.bookmark import Bookmark
from app.models.learning_progress import LearningProgress
from app.models.upload import Upload, ResourceType, UploadStatus
from app.models.notebook import Notebook
from app.models.chat_history import ChatHistory
from app.models.memory import Memory
from app.models.ai_config import AIConfiguration

__all__ = [
    "Base",
    "BaseModel",
    "UserRole",
    "User",
    "Course",
    "Module",
    "Note",
    "NoteStatus",
    "NoteEvaluation",
    "Quiz",
    "QuizAttempt",
    "Bookmark",
    "LearningProgress",
    "Upload",
    "ResourceType",
    "UploadStatus",
    "Notebook",
    "ChatHistory",
    "Memory",
    "AIConfiguration",
]
