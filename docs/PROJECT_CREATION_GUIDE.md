# AI-First Project Creation Guide

## Goal

Build an AI-first service that takes a PDF, understands its layout and meaning, and returns validated structured JSON. For this repository, the target is not just OCR. The target is semantic extraction: ticket metadata, entities, amounts, dates, selections, and other fields must be normalized into a stable schema.

## When a maximal-AI approach makes sense

- PDF layouts come from multiple sources and change often.
- Some documents are scans, screenshots, or image-heavy PDFs.
- The extraction target is semantic, not only positional.
- The team wants to add new document types without rewriting many regex rules.
- A human review step or confidence score is acceptable.

If the input format is always the same and highly stable, a rule-based parser is cheaper. If the format varies, AI should be the center of the pipeline and deterministic code should act as the safety layer.

## Recommended architecture

1. Ingestion layer
   Accept PDF bytes, file metadata, source identifier, and request ID.
2. Preprocessing layer
   Split the PDF into pages, render page images, extract any embedded text, and preserve page order.
3. OCR and layout layer
   Use a document AI service or multimodal model to recover text, blocks, tables, and reading order.
4. Document classification layer
   Detect the document family before extraction. Different prompt templates and validation rules should be used for different document types.
5. Schema-guided extraction layer
   Ask an LLM to map the recovered content into a strict JSON schema.
6. Validation and normalization layer
   Convert strings to numbers, normalize dates, standardize currencies, and reject invalid outputs.
7. Confidence and review layer
   Mark low-confidence fields, missing required values, or conflicting values for manual review.
8. Output layer
   Return JSON plus trace metadata: model used, prompt version, page references, confidence, and validation warnings.

## Recommended default stack

For a maximal-AI version of this project, the most practical stack is:

- Runtime: Python 3.11+.
- API surface: local CLI entrypoint or FastAPI.
- OCR and layout: a lightweight PDF text or parsing layer such as pypdf, pdfplumber, LlamaParse, or Docling before the LLM stage.
- Semantic structuring: a multimodal GPT or Claude model with strict JSON output.
- Contracts: Pydantic models for input, output, and validation errors.
- Retries: Tenacity for transient provider failures.
- Observability: structured logs, request IDs, prompt versioning, response timing, and model/provider tags.
- Storage for debugging: raw OCR output, prompt payload, model output, normalized JSON, and validation report.

## Best extraction pattern

The strongest pattern for this kind of product is hybrid, not purely prompt-driven:

1. Use OCR or layout AI to recover the text and document structure.
2. Build a compact, schema-aware prompt from the recovered content.
3. Ask the LLM to return only JSON, never prose.
4. Re-validate every field in code.
5. Save both the raw evidence and the normalized output.

This keeps AI responsible for semantic interpretation while code remains responsible for trust, repeatability, and type safety.

## Proposed project structure

```text
src/
  main.py
  api/
    handlers.py
  domain/
    schemas.py
    document_types.py
    validation.py
  services/
    pdf_loader.py
    layout_extractor.py
    llm_extractor.py
    normalizer.py
    confidence.py
      structural_ai_evaluator.py
  providers/
    openai_extractor.py
    anthropic_extractor.py
  prompts/
    classify_document.txt
    extract_structured_json.txt
  tests/
    fixtures/
    test_sample_pdf.py
```

## Implementation order

1. Define the target schema first.
   Decide which fields are required, optional, numeric, normalized, and review-only.
2. Add sample fixtures.
   Keep at least one golden PDF and one expected JSON output.
3. Build a PDF preprocessing adapter.
   Extract pages, page images, raw text, and metadata in one standard internal format.
4. Add one OCR or layout provider.
   Start with a single provider instead of abstracting everything on day one.
5. Add one LLM extraction provider.
   Make it return strict JSON that matches the schema exactly.
6. Add deterministic normalization.
   Dates, money, percentages, booleans, and identifiers should be normalized in code.
7. Add validation and confidence scoring.
   Missing required fields, impossible totals, or broken number parsing should fail clearly.
8. Add evaluation scripts.
   Compare extracted JSON against expected JSON and track field-level accuracy.
9. Add observability.
   Every request should be traceable from input PDF to final JSON.

## Environment variables to plan for

```text
AI_PROVIDER=
LLM_PROVIDER=
LLM_MODEL=
AI_BASE_URL=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
LOG_LEVEL=
STORE_DEBUG_ARTIFACTS=
```

Only one provider pair is needed to start, but the interface should allow provider replacement later.

## Prompt design rules

- Give the model a single extraction task.
- Provide the exact JSON schema or a structurally equivalent description.
- Include page identifiers and, if available, bounding box references.
- Explicitly forbid prose, commentary, and invented values.
- Instruct the model to output `null` for missing fields.
- Provide a short example only if it materially improves consistency.

## Validation rules that should never be skipped

- Required fields must be present or explicitly null.
- Numeric fields must parse to numeric types in code.
- Date fields must be converted to one canonical format.
- Currency amounts must preserve sign and decimal precision.
- Conflicting values found in multiple locations must raise a warning.
- The final output must conform to one Pydantic schema.

## What to log for each request

- Request ID.
- File name and checksum.
- OCR provider and version.
- LLM provider, model, and prompt version.
- Latency of each stage.
- Validation failures.
- Confidence score.
- Manual review flag.

## Definition of done

A first usable version of the project should satisfy all points below:

- One PDF can be processed end to end.
- The output matches a defined JSON schema.
- The pipeline stores enough evidence to debug bad extractions.
- Low-confidence results are visible instead of silently accepted.
- A fixture-based test can verify the sample document.
- The extraction flow can swap providers without rewriting domain logic.

## Recommended first release for this repository

For this repository, the highest-value first release is:

- Local Python entrypoint or FastAPI endpoint.
- pypdf, LlamaParse, or Docling as the document ingestion layer.
- GPT or Claude for schema-guided normalization.
- Pydantic validation.
- Structural AI Evaluator for post-extraction schema review.
- One golden fixture for the sample PDF.
- Manual review output for uncertain fields.

That path maximizes AI usage while still keeping the system debuggable and production-oriented.