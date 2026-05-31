from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_DIR = ROOT_DIR / "src" / "data" / "inbox"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "src" / "data" / "outbox"


@dataclass(frozen=True)
class Settings:
    ai_api_key: str
    ai_base_url: str | None
    extraction_model: str
    evaluator_model: str
    input_dir: Path
    output_dir: Path
    max_text_chars: int
    request_timeout_seconds: int
    store_raw_text: bool


def load_settings() -> Settings:
    load_dotenv(ROOT_DIR / ".env")

    input_dir = DEFAULT_INPUT_DIR
    output_dir = DEFAULT_OUTPUT_DIR

    return Settings(
        ai_api_key=os.getenv("AI_API_KEY"),
        ai_base_url=os.getenv("AI_BASE_URL", ""),
        extraction_model=os.getenv("AI_EXTRACTION_MODEL") or "gpt-4.1-mini",
        evaluator_model=os.getenv("AI_EVALUATOR_MODEL") or "gpt-4.1-mini",
        input_dir=input_dir,
        output_dir=output_dir,
        max_text_chars=int(os.getenv("MAX_TEXT_CHARS", "20000")),
        request_timeout_seconds=max(int(os.getenv("REQUEST_TIMEOUT_SECONDS", "180")), 180),
        store_raw_text=False,
    )
