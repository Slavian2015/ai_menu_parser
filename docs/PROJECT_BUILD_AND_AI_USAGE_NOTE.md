# Project Build And AI Usage Note

## Human-AI Development Process

This project was developed as an iterative collaboration between me and GitHub Copilot in VS Code. I used the AI assistant as a design, implementation, and debugging partner, while the direction, constraints, and final decisions remained under my control. The work did not begin with code. It began with reading the take-home assignment, reviewing the sample input, and clarifying what the system was actually supposed to return.

The first stage was problem framing. I asked the AI assistant to read the task and suggest two possible solution directions. That helped compare a more conventional parsing approach with a more AI-heavy extraction pipeline. After reviewing those options, I chose the second direction: maximize AI usage for semantic understanding, but keep validation, normalization, and error handling in deterministic Python code.

The second stage was defining working rules before writing implementation code. Together, we wrote down engineering principles for the repository, including schema-first design, strict JSON output, provider isolation, observable failures, and the rule that AI should be used for meaning while code should be used for trust. Those principles were captured in the repository guidance and used as the baseline for later design decisions.

The third stage was building the first end-to-end version of the pipeline. With AI assistance, the project structure, documentation, prompt layer, provider client, PDF text extraction flow, schema validation, and structural evaluation logic were created. The initial working version successfully extracted data from PDF text, but it produced a fairly large generic object with metadata, fields, items, warnings, and supporting information.

The fourth stage was iterative correction. As implementation progressed, I used the AI assistant to debug environment issues, dependency problems, model configuration, timeout and retry behavior, and JSON cleanup. This part of the workflow was highly interactive: I ran the code, reviewed failures, asked for targeted fixes, and adjusted the system step by step until the pipeline ran end to end.

The final major stage happened late in the process, when the project was already close to complete. At that point, it became clear that the output structure was too large for the real assignment need. The essential requirement was much simpler: a menu dataset in the shape of a top-level `data` array containing `category`, `dish_name`, `price`, `description`, and `dish_id`. Because of that clarification, the schema, prompt, and normalization logic were refactored near the end of the project so that the final output matched the actual business requirement instead of the earlier generic document contract.

The final result is a local extraction workflow that reads PDFs from `src/data/inbox` and writes compact structured JSON to `src/data/outbox` in the form:

```json
{
  "data": [
    {
      "category": "BURGERS",
      "dish_name": "ALL AMERICAN BURGER",
      "price": "$17",
      "description": "...",
      "dish_id": "001"
    }
  ]
}
```

## Use Of AI Tools

- GitHub Copilot in VS Code was used to review the assignment, compare solution directions, define project rules, draft code, refactor modules, update prompts, and debug failures during development.
- An OpenAI-compatible model was used inside the application for semantic menu extraction and for optional structural evaluation of the JSON returned by the extraction stage.
- AI-generated suggestions were not used as-is; they were adapted to a schema-first design and later revised when the original output structure proved broader than the actual assignment requirement.
- The main assumption is that the input PDF contains extractable text; the current version does not yet include a full OCR and layout-recovery pipeline for scanned image-based documents.
- Known gaps and edge cases include noisy multi-column menus, ambiguous category boundaries, and modifier or add-on text that appears near menu items without a clearly separate price.

## Final Outcome

The project ended as a practical AI-assisted PDF parsing system with a documented development process, explicit engineering principles, deterministic validation, and a simplified output format focused on menu items only. The final deliverable is not just a prompt. It is a small end-to-end pipeline that shows the full path from problem analysis and rule-setting to implementation, debugging, and late-stage schema correction.