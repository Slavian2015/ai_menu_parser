from __future__ import annotations

from typing import Any

from src.config import Settings
from src.prompts import EXTRACTION_SYSTEM_PROMPT, build_extraction_user_prompt
from src.providers.openai_client import OpenAIJsonClient
from src.services.pdf_text_extractor import PdfTextDocument


class StructuredDataExtractor:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = OpenAIJsonClient(
            api_key=settings.ai_api_key,
            base_url=settings.ai_base_url,
            model=settings.extraction_model,
            timeout_seconds=settings.request_timeout_seconds,
        )

    def extract(self, pdf_document: PdfTextDocument) -> dict[str, Any]:
        prompt = build_extraction_user_prompt(
            source_name=pdf_document.file_name,
            pdf_text=pdf_document.as_prompt_text(self._settings.max_text_chars),
        )

        payload = self._client.generate_json(
            system_prompt=EXTRACTION_SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        return _normalize_menu_payload(payload)


def _normalize_menu_payload(payload: dict[str, Any]) -> dict[str, Any]:
    raw_items = payload.get("data")
    if not isinstance(raw_items, list):
        raw_items = payload.get("items")

    if not isinstance(raw_items, list):
        return {"data": []}

    normalized_items: list[dict[str, Any]] = []
    for raw_item in raw_items:
        normalized_item = _normalize_menu_item(raw_item)
        if normalized_item is not None:
            normalized_item["dish_id"] = f"{len(normalized_items) + 1:03d}"
            normalized_items.append(normalized_item)

    return {"data": normalized_items}


def _normalize_menu_item(raw_item: Any) -> dict[str, Any] | None:
    if not isinstance(raw_item, dict):
        return None

    attributes = raw_item.get("attributes") if isinstance(raw_item.get("attributes"), dict) else {}

    category = _clean_text(raw_item.get("category") or attributes.get("category"))
    dish_name = _clean_text(raw_item.get("dish_name") or raw_item.get("label"))
    description = _clean_text(raw_item.get("description") or attributes.get("description"))
    price = _normalize_price(
        raw_item.get("price"),
        raw_item.get("amount"),
        attributes.get("listed_price"),
    )

    if not dish_name or not price:
        return None

    return {
        "category": (category or "UNCATEGORIZED").upper(),
        "dish_name": dish_name,
        "price": price,
        "description": description,
        "dish_id": "000",
    }


def _normalize_price(*values: Any) -> str | None:
    for value in values:
        if value is None:
            continue

        if isinstance(value, (int, float)):
            numeric_value = float(value)
            if numeric_value.is_integer():
                return f"${int(numeric_value)}"
            return f"${numeric_value:.2f}"

        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                continue
            if stripped.startswith("$"):
                return stripped
            return f"${stripped}"

    return None


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    return text or None