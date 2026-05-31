# ai_menu_parser
AI PDF file reader to extract structured data


## Project Docs

- [AI-first project creation guide](docs/PROJECT_CREATION_GUIDE.md)
- [AI tools for PDF structuring and parsing](docs/AI_PDF_EXTRACTION_OPTIONS.md)
- [Agent coding rules for GPT and Claude Code](AGENTS.md)


# Start the project

1. **Create virtual environment with `venv` and activate it**:
   1. `python -m venv .venv`
   2. Activate:
    - for Windows `.\.venv\Scripts\Activate.ps1`
    - for Linux, macOS `source .venv/bin/activate`
  
2. **Install Requirements**:
   1. `pip install -r requirements.txt`

3. **Prepare env file**:
   1. `cp .env.dist .env`
   2. Fill `AI_API_KEY`
   3. Optionally set `AI_BASE_URL`, `AI_EXTRACTION_MODEL`, and `AI_EVALUATOR_MODEL`

4. **Use the data folders**:
   1. Put input PDFs into `src/data/inbox`
   2. Structured JSON and evaluation reports will be written to `src/data/outbox`

5. **Run the pipeline**:
   1. Process all PDFs in inbox: `python -m src.main`
   2. Process one PDF: `python -m src.main --file "src/data/inbox/espn_bet (1).pdf"`
   3. Evaluate existing JSON only: `python -m src.main --evaluate-json path/to/result.json`

## Current Structure

```text
src/
  data/
    inbox/
    outbox/
  domain/
  providers/
  services/
  main.py
```