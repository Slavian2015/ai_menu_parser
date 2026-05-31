from __future__ import annotations

import json
import re
from typing import Any
from openai import OpenAI


class OpenAIJsonClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str | None = None,
        timeout_seconds: int = 90,
        max_retries: int = 0,
    ) -> None:
        if not api_key:
            raise ValueError("AI_API_KEY is required for AI extraction.")

        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=max(timeout_seconds, 180),
            max_retries=max_retries,
        )
        self._model = model

    @property
    def model(self) -> str:
        return self._model

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        response = self._client.chat.completions.create(
            model=self._model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = response.choices[0].message.content or "{}"
        normalized_content = _normalize_json_content(content)
        payload = json.loads(normalized_content)

        if not isinstance(payload, dict):
            raise TypeError("The AI provider returned a non-object JSON payload.")

        return payload


def _normalize_json_content(raw_content: str) -> str:
    content = raw_content.strip().lstrip("\ufeff")
    if not content:
        return "{}"

    content = _strip_markdown_fences(content)
    content = _strip_json_label(content)
    content = _unwrap_quoted_json(content)

    extracted_object = _extract_first_json_object(content)
    if extracted_object is not None:
        return extracted_object

    return content


def _strip_markdown_fences(content: str) -> str:
    if not content.startswith("```"):
        return content

    lines = content.splitlines()
    if not lines:
        return content

    lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    return "\n".join(lines).strip()


def _strip_json_label(content: str) -> str:
    return re.sub(r"^\s*json\s*[:\-]?\s*", "", content, count=1, flags=re.IGNORECASE)


def _unwrap_quoted_json(content: str) -> str:
    stripped = content.strip()
    if (
        len(stripped) < 2
        or stripped[0] != stripped[-1]
        or stripped[0] not in {'"', "'"}
    ):
        return stripped

    if stripped[0] == '"':
        try:
            decoded = json.loads(stripped)
        except json.JSONDecodeError:
            decoded = stripped[1:-1]
    else:
        decoded = stripped[1:-1]

    if isinstance(decoded, str):
        return decoded.strip()

    return stripped


def _extract_first_json_object(content: str) -> str | None:
    start_index = content.find("{")
    if start_index == -1:
        return None

    depth = 0
    in_string = False
    escape_next = False

    for index in range(start_index, len(content)):
        char = content[index]

        if escape_next:
            escape_next = False
            continue

        if char == "\\":
            escape_next = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return content[start_index : index + 1]

    return None
