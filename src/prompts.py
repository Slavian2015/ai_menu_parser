from __future__ import annotations

import json
from typing import Any

from src.domain.schemas import EvaluatorFeedback, StructuredDocument


EXTRACTION_SYSTEM_PROMPT = """You extract structured JSON from PDF text.

Rules:
- Return JSON only.
- Do not wrap the response in markdown.
- Follow the requested schema exactly.
- Keep only the requested `data` array.
- Use null for missing scalar values.
- Do not invent facts that are not supported by the provided text.
- Omit sections, metadata, evidence, warnings, and analysis text.
"""


STRUCTURAL_EVALUATION_SYSTEM_PROMPT = """You are Structural AI Evaluator.

You review JSON against a target schema and focus only on structural quality.

Rules:
- Evaluate structure, types, required sections, null handling, and shape consistency.
- Do not judge whether the extracted values are factually correct relative to the PDF.
- Return JSON only.
- If the payload is structurally weak, list concrete issues with JSON paths.
"""


EXTRACTION_OUTPUT_TEMPLATE = {
    "data": [
        {
            "category": "string",
            "dish_name": "string",
            "price": "string|null",
            "description": "string|null",
            "dish_id": "001",
        }
    ]
}


def build_extraction_user_prompt(source_name: str, pdf_text: str) -> str:
    schema_template = json.dumps(EXTRACTION_OUTPUT_TEMPLATE, ensure_ascii=False, indent=2)

    return f"""Extract menu items from the PDF text below.

Source file: {source_name}

Return one JSON object with exactly this shape:
{schema_template}

Important extraction rules:
- Return only the `data` array inside the top-level object.
- Each entry must contain exactly: `category`, `dish_name`, `price`, `description`, `dish_id`.
- `category` should be the menu section name in uppercase, for example `BURGERS`.
- `dish_name` should contain only the item name.
- `price` should preserve the printed menu value, for example `$17` or `$X`.
- `description` should contain the menu description text when present.
- `dish_id` must be a zero-padded sequential identifier like `001`, `002`, `003`.
- Include only real sellable menu entries.
- Exclude advisory text, section headers, service notes, sauces, rubs, and other entries without a listed price.
- Use `null` only when a real menu item is missing a description or printed price.

PDF text:
{pdf_text}
"""


def build_structural_evaluation_user_prompt(candidate_payload: dict[str, Any]) -> str:
    schema_json = json.dumps(StructuredDocument.model_json_schema(), ensure_ascii=False, indent=2)
    evaluation_json = json.dumps(EvaluatorFeedback.model_json_schema(), ensure_ascii=False, indent=2)
    candidate_json = json.dumps(candidate_payload, ensure_ascii=False, indent=2, default=str)

    return f"""Review the candidate JSON against the target schema.

Target schema:
{schema_json}

Return your review using this JSON schema:
{evaluation_json}

Candidate JSON:
{candidate_json}

Focus on:
- missing top-level `data` array
- wrong data types
- missing required item keys
- non-string prices or dish names
- invalid `dish_id` format
- entries that are not menu items

Use JSON paths such as `$.data[0].price` or `$.data[0].dish_id`.
"""