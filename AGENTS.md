# AGENTS.md

## Project Intent

This repository should evolve into an AI-first PDF extraction system that converts PDFs into validated structured JSON. The system must use AI for semantic understanding and conventional code for validation, normalization, observability, and failure handling.

## Primary Engineering Goal

Maximize extraction quality without hiding uncertainty. The system is allowed to be AI-heavy, but it must remain debuggable, testable, and safe to extend.

## Working Principles For GPT And Claude Code

### 1. Schema before prompt

Define the target output schema before changing prompts or providers. No prompt should be treated as the contract. The schema is the contract.

### 2. AI for meaning, code for trust

Use AI to understand document meaning, classify document types, and map messy text into semantic fields. Use Python code to enforce types, ranges, required fields, normalization rules, and conflict checks.

### 3. Preserve source evidence

Never discard raw OCR text, layout blocks, page numbers, or source snippets that support extracted values. Every high-value field should remain traceable to source evidence.

### 4. Prefer layered extraction over one-shot magic

Preferred order:

1. preprocess PDF
2. recover OCR and layout
3. classify document type
4. run schema-guided extraction
5. normalize and validate
6. score confidence and flag review cases

### 5. Keep provider-specific logic isolated

Provider adapters belong in a dedicated providers layer. Domain schemas, normalization, and validation must stay provider-agnostic.

### 6. Never trust free-form model output

Models should return strict JSON only. If the provider supports structured output or tool calling, use it. If not, validate the raw JSON aggressively and fail loudly.

### 7. Favor observable failures over silent corruption

If a required field is missing or conflicting, surface a validation error or review flag. Do not silently invent defaults for business-critical values.

## Code Style

- Use Python type hints everywhere.
- Use Pydantic models for request and response contracts.
- Prefer small, composable functions with clear inputs and outputs.
- Keep prompts out of business logic modules.
- Put normalization and validation in deterministic code.
- Avoid hidden global state.
- Prefer explicit provider interfaces over ad hoc conditionals.
- Keep file and function names descriptive.

## Prompt Style

- Give the model one task at a time.
- Provide the exact output schema.
- Instruct the model to return only JSON.
- Tell the model to use null for missing fields.
- Pass page IDs and source fragments when available.
- Forbid explanations, summaries, and narrative text in the final output.
- Use short examples only when they improve consistency materially.

## Testing Rules

- Maintain at least one golden PDF fixture and one expected JSON result.
- Add regression tests whenever a prompt or provider adapter changes.
- Validate field-level correctness, not just document-level success.
- Test missing fields, malformed numbers, conflicting values, and low-confidence paths.

## Observability Rules

For every extraction request, capture:

- request ID
- file name or checksum
- provider names and model IDs
- prompt version
- stage latencies
- validation errors
- confidence score
- manual review flag

## Review Checklist For Future Changes

Before accepting a change, verify:

1. the schema is still explicit and versioned
2. extracted values remain traceable to source evidence
3. provider-specific code did not leak into the domain layer
4. prompts still target strict JSON
5. validation rules still run after AI output
6. fixtures or regression tests were updated when behavior changed

## Non-Goals

- Do not optimize for clever prompts over system design.
- Do not bury extraction logic inside giant prompts.
- Do not couple the whole system to a single AI vendor.
- Do not skip validation because a model looks accurate on one sample.

## Default Bias For This Repository

When choosing between two designs, prefer the one that is:

- easier to audit
- easier to test
- easier to swap providers in
- clearer about uncertainty
- safer for structured data extraction