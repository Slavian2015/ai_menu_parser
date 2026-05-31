from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from src.config import Settings
from src.domain.schemas import (
    EvaluatorFeedback,
    StructuralEvaluationReport,
    StructuralIssue,
    StructuredDocument,
    utc_timestamp,
)
from src.prompts import (
    STRUCTURAL_EVALUATION_SYSTEM_PROMPT,
    build_structural_evaluation_user_prompt,
)
from src.providers.openai_client import OpenAIJsonClient


class StructuralAIEvaluator:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def evaluate(self, candidate_payload: dict[str, Any]) -> StructuralEvaluationReport:
        issues: list[StructuralIssue] = []
        deterministic_valid = True

        try:
            StructuredDocument.model_validate(candidate_payload)
        except ValidationError as exc:
            deterministic_valid = False
            issues.extend(self._map_validation_errors(exc))

        ai_feedback: EvaluatorFeedback | None = None
        skipped_reason: str | None = None

        if self._settings.ai_api_key:
            try:
                client = OpenAIJsonClient(
                    api_key=self._settings.ai_api_key,
                    base_url=self._settings.ai_base_url,
                    model=self._settings.evaluator_model,
                    timeout_seconds=self._settings.request_timeout_seconds,
                )
                ai_payload = client.generate_json(
                    system_prompt=STRUCTURAL_EVALUATION_SYSTEM_PROMPT,
                    user_prompt=build_structural_evaluation_user_prompt(candidate_payload),
                )
                ai_feedback = EvaluatorFeedback.model_validate(ai_payload)
            except Exception as exc:
                skipped_reason = f"AI evaluation skipped because the evaluator call failed: {exc}"
        else:
            skipped_reason = "AI evaluation skipped because no API key is configured."

        if ai_feedback:
            issues.extend(ai_feedback.issues)

        passed = deterministic_valid and (ai_feedback.passed if ai_feedback else True)

        if ai_feedback:
            score = min(ai_feedback.score, 1.0 if deterministic_valid else 0.0)
        else:
            score = 1.0 if deterministic_valid else 0.0

        summary = self._build_summary(deterministic_valid, ai_feedback, skipped_reason)

        return StructuralEvaluationReport(
            schema_name=StructuredDocument.__name__,
            checked_at=utc_timestamp(),
            passed=passed,
            score=score,
            deterministic_valid=deterministic_valid,
            ai_valid=ai_feedback.passed if ai_feedback else None,
            checked_by_model=self._settings.evaluator_model if ai_feedback else None,
            skipped_reason=skipped_reason,
            summary=summary,
            issues=issues,
        )

    def _map_validation_errors(self, error: ValidationError) -> list[StructuralIssue]:
        mapped_errors: list[StructuralIssue] = []

        for item in error.errors():
            path = "$"
            if item.get("loc"):
                path += "." + ".".join(str(part) for part in item["loc"])

            mapped_errors.append(
                StructuralIssue(
                    code=item.get("type", "validation_error"),
                    severity="error",
                    path=path,
                    message=item.get("msg", "Schema validation failed."),
                    recommendation="Return JSON that matches the structured schema exactly.",
                )
            )

        return mapped_errors

    def _build_summary(
        self,
        deterministic_valid: bool,
        ai_feedback: EvaluatorFeedback | None,
        skipped_reason: str | None,
    ) -> str:
        if ai_feedback and ai_feedback.summary:
            return ai_feedback.summary
        if deterministic_valid and not skipped_reason:
            return "The payload passed deterministic schema validation and AI structural review."
        if deterministic_valid:
            return "The payload passed deterministic schema validation, but AI structural review was skipped."
        return "The payload does not conform to the expected structured schema."