import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User



class ResourceType(str, enum.Enum):
    NOTES = "notes"
    VIDEOS = "videos"
    LAB_MANUALS = "lab_manuals"
    BOOKS = "books"
    PYQS = "pyqs"


class UploadStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    INDEXED = "INDEXED"
    FAILED = "FAILED"


class Upload(BaseModel):
    __tablename__ = "uploads"

    # Owner
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Subject slug, e.g. "power-system", "power-electronics"
    subject_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # Resource category
    resource_type: Mapped[ResourceType] = mapped_column(
        SAEnum(ResourceType, name="resourcetype", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    # File metadata
    original_name: Mapped[str] = mapped_column(String(512), nullable=False)   # user-facing name
    filename: Mapped[str] = mapped_column(String(512), nullable=False)         # stored filename (uuid-based)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    minio_key: Mapped[str] = mapped_column(String(1024), nullable=False)       # MinIO object key
    status: Mapped[UploadStatus] = mapped_column(
        SAEnum(UploadStatus, name="uploadstatus", values_callable=lambda x: [e.value for e in x]),
        default=UploadStatus.UPLOADED,
        nullable=False,
        index=True,
    )

    # Relationships
    uploaded_by: Mapped["User"] = relationship(back_populates="uploads")

    def __repr__(self) -> str:
        return f"<Upload id={self.id} original_name={self.original_name} type={self.resource_type}>"
