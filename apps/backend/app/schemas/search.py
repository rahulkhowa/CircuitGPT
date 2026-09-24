from typing import Any

from pydantic import BaseModel, Field


class SearchCategoryFilter(str):
    ALL = "all"
    NOTES = "notes"
    FORMULAS = "formulas"
    CIRCUITS = "circuits"
    PYQS = "pyqs"
    LABS = "labs"
    CHAT = "chat"


class SearchQuery(BaseModel):
    query: str = Field(..., json_schema_extra={"example": "KCL Kirchhoff Current Law"})
    category: str | None = Field(default="all", json_schema_extra={"example": "all"})
    subject_id: str | None = Field(None, json_schema_extra={"example": "ee101"})
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SearchResultItem(BaseModel):
    id: str
    title: str
    category: str
    subject_id: str
    subject_name: str
    snippet: str
    score: float
    link: str
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    query: str
    category: str
    total_matches: int
    items: list[SearchResultItem]
