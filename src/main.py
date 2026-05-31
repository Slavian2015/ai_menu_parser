from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any

from src.config import Settings, load_settings
from src.domain.schemas import StructuredDocument
from src.services.pdf_text_extractor import PdfTextExtractor
from src.services.structured_extractor import StructuredDataExtractor
from src.services.structural_ai_evaluator import StructuralAIEvaluator


LOGGER = logging.getLogger(__name__)
OUTPUT_FILE = "output.json"


def main() -> int:
	configure_logging()
	settings = load_settings()
	settings.output_dir.mkdir(parents=True, exist_ok=True)

	evaluator = StructuralAIEvaluator(settings)

	if not settings.ai_api_key:
		raise SystemExit("AI_API_KEY is required to run PDF extraction.")

	extractor = StructuredDataExtractor(settings)
	pdf_text_extractor = PdfTextExtractor()
	pdf_files = sorted(path for path in settings.input_dir.glob("*.pdf") if path.is_file())

	if not pdf_files:
		LOGGER.warning("No PDF files found in %s", settings.input_dir)
		return 0

	exit_code = 0
	for pdf_path in pdf_files:
		try:
			process_pdf(pdf_path, settings, pdf_text_extractor, extractor, evaluator)
		except Exception as exc:
			exit_code = 1
			LOGGER.exception("Failed to process %s", pdf_path.name)
			write_json(
				settings.output_dir / f"{pdf_path.stem}.error.json",
				{
					"file": pdf_path.name,
					"error_type": exc.__class__.__name__,
					"message": str(exc),
				},
			)

	return exit_code


def process_pdf(
	pdf_path: Path,
	settings: Settings,
	pdf_text_extractor: PdfTextExtractor,
	extractor: StructuredDataExtractor,
	evaluator: StructuralAIEvaluator,
) -> None:
	LOGGER.info("Processing %s", pdf_path.name)
	pdf_document = pdf_text_extractor.extract(pdf_path)
	candidate_payload = extractor.extract(pdf_document)
	report = evaluator.evaluate(candidate_payload)

	if report.deterministic_valid:
		structured_payload = StructuredDocument.model_validate(candidate_payload).model_dump(mode="json")
	else:
		structured_payload = candidate_payload

	write_json(settings.output_dir / f"{pdf_path.stem}.structured.json", structured_payload)
	write_json(settings.output_dir / f"{pdf_path.stem}.evaluation.json", report.model_dump(mode="json"))

	if settings.store_raw_text:
		raw_text_path = settings.output_dir / f"{pdf_path.stem}.raw.txt"
		raw_text_path.write_text(pdf_document.text, encoding="utf-8")


def write_json(file_path: Path, payload: dict[str, Any]) -> None:
	file_path.write_text(
		json.dumps(payload, ensure_ascii=False, indent=2),
		encoding="utf-8",
	)


def configure_logging() -> None:
	logging.basicConfig(
		level=logging.INFO,
		format="%(levelname)s %(name)s: %(message)s",
	)


if __name__ == "__main__":
	raise SystemExit(main())
