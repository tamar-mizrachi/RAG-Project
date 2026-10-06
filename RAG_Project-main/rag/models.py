from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel, Field


SourceType = Literal["cursor", "kiro", "claude_code", "unknown"]
ItemType = Literal["decision", "rule", "warning", "change"]


class SourceInfo(BaseModel):
    tool: SourceType
    file: str
    heading: Optional[str] = None
    line_range: Optional[list[int]] = None
    observed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class KnowledgeItem(BaseModel):
    id: str
    type: ItemType
    title: str
    summary: str
    tags: list[str] = Field(default_factory=list)
    source: SourceInfo


class StructuredKnowledge(BaseModel):
    schema_version: str = "1.0"
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    decisions: list[KnowledgeItem] = Field(default_factory=list)
    rules: list[KnowledgeItem] = Field(default_factory=list)
    warnings: list[KnowledgeItem] = Field(default_factory=list)
    changes: list[KnowledgeItem] = Field(default_factory=list)


class RouteDecision(BaseModel):
    route: Literal["semantic", "structured"]
    reason: str


class RetrievedChunk(BaseModel):
    text: str
    score: Optional[float] = None
    source: dict = Field(default_factory=dict)


class WorkflowResult(BaseModel):
    answer: str
    route: str
    confidence: float
    sources: list[dict] = Field(default_factory=list)
