from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.upload import Upload, ResourceType
from app.schemas.search import (
    SearchQuery,
    SearchResponse,
    SearchResultItem,
)

SYSTEM_TITLES = {
    "power-system": "Power System (EE-PS)",
    "power-electronics": "Power Electronics (EE-PE)",
    "machine-system": "Machine System (EE-MS)",
    "network-system": "Network System (EE-NS)",
    "control-system": "Control System (EE-CS)",
}


class HybridSearchService:
    """
    Hybrid Search service searching real uploaded resources and system documents.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def search(self, query_params: SearchQuery) -> SearchResponse:
        q = (query_params.query or "").strip().lower()
        category = query_params.category or "all"
        subject_id = query_params.subject_id

        stmt = select(Upload)

        # Filter by subject if specified
        if subject_id and subject_id != "all":
            stmt = stmt.where(Upload.subject_id == subject_id)

        # Filter by resource type / category if specified
        if category and category != "all":
            try:
                rt = ResourceType(category)
                stmt = stmt.where(Upload.resource_type == rt)
            except ValueError:
                pass

        # Filter by query if specified
        if q:
            stmt = stmt.where(Upload.original_name.ilike(f"%{q}%"))

        stmt = stmt.order_by(Upload.created_at.desc()).limit(query_params.limit).offset(query_params.offset)

        result = await self.db.execute(stmt)
        uploads = result.scalars().all()

        items: List[SearchResultItem] = []
        for u in uploads:
            sub_name = SYSTEM_TITLES.get(u.subject_id, u.subject_id)
            items.append(
                SearchResultItem(
                    id=str(u.id),
                    title=u.original_name,
                    category=u.resource_type.value if hasattr(u.resource_type, "value") else str(u.resource_type),
                    subject_id=u.subject_id,
                    subject_name=sub_name,
                    snippet=f"{u.resource_type.value.replace('_', ' ').title() if hasattr(u.resource_type, 'value') else u.resource_type} • {u.mime_type}",
                    score=0.95,
                    link=f"/dashboard/subjects/{u.subject_id}",
                    tags=[u.subject_id, u.resource_type.value if hasattr(u.resource_type, "value") else str(u.resource_type)],
                    metadata={
                        "upload_id": str(u.id),
                        "file_size_bytes": u.file_size_bytes,
                        "status": str(u.status.value if hasattr(u.status, "value") else u.status),
                    },
                )
            )

        return SearchResponse(
            query=query_params.query,
            category=category,
            total_matches=len(items),
            items=items,
        )

