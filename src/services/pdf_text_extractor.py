from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class PdfPageText:
    page_number: int
    text: str


@dataclass(frozen=True)
class PdfTextDocument:
    file_name: str
    page_count: int
    pages: list[PdfPageText]
    text: str

    def as_prompt_text(self, max_chars: int) -> str:
        if len(self.text) <= max_chars:
            return self.text

        clipped_text = self.text[:max_chars].rstrip()
        return f"{clipped_text}\n\n[TRUNCATED: input was clipped to fit the model budget]"


class PdfTextExtractor:
    def extract(self, pdf_path: Path) -> PdfTextDocument:
        reader = PdfReader(str(pdf_path))
        pages: list[PdfPageText] = []

        for index, page in enumerate(reader.pages, start=1):
            page_text = (page.extract_text() or "").strip()
            if page_text:
                pages.append(PdfPageText(page_number=index, text=page_text))

        combined_text = "\n\n".join(
            f"--- Page {page.page_number} ---\n{page.text}" for page in pages
        ).strip()

        if not combined_text:
            raise ValueError(
                f"No extractable text was found in {pdf_path.name}. Add OCR before the AI extraction step."
            )

        return PdfTextDocument(
            file_name=pdf_path.name,
            page_count=len(reader.pages),
            pages=pages,
            text=combined_text,
        )