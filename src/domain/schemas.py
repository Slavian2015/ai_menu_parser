from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MenuDataItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: str
    dish_name: str
    price: str | None = None
    description: str | None = None
    dish_id: str = Field(pattern=r"^\d{3}$")


class StructuredDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: list[MenuDataItem] = Field(default_factory=list)


class StructuralIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    severity: Literal["info", "warning", "error"]
    path: str
    message: str
    recommendation: str | None = None


class EvaluatorFeedback(BaseModel):
    model_config = ConfigDict(extra="forbid")

    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    summary: str | None = None
    issues: list[StructuralIssue] = Field(default_factory=list)


class StructuralEvaluationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_name: str
    checked_at: str
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    deterministic_valid: bool
    ai_valid: bool | None = None
    checked_by_model: str | None = None
    skipped_reason: str | None = None
    summary: str | None = None
    issues: list[StructuralIssue] = Field(default_factory=list)


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()
