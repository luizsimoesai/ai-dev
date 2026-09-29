# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal collection of small, working AI/LLM example scripts and notebooks, organized by **concept** rather than by provider or framework, so code stays easy to adapt and compare. This is not a single application — there is no shared entry point, build, or test suite across the repo.

## Repository layout

- `models/` — direct usage of each provider SDK (OpenAI, Anthropic, Ollama): what actually differs from SDK to SDK.
- `techniques/` — provider-agnostic techniques: RAG from scratch, agentic RAG, prompt engineering, a ReAct agent built from scratch, typed classification, etc.
- `fundamentals/` — embeddings, document parsing, vector databases, NLP fundamentals.
- `mcp/` — Model Context Protocol recipes: server setup, client usage, function-calling comparisons, Docker packaging.
- `tools/` — supporting tooling: uv, deployment (Docker, Google Cloud), scraping (Firecrawl), Python utilities.
- `_archive/` — content outside the scope of AI recipes (general Python/dev tutorials, third-party course copies), kept for reference only — do not treat as active code.

Each numbered recipe directory (e.g. `techniques/agentic-rag/1-build-tools.py`, `2-import-tools.py`, ...) is a progressive walkthrough: later files build on earlier ones and often import shared helpers from a local `utils/` subfolder. Read the recipe's own `README.md` before editing — it documents what each numbered file demonstrates.

## Running code

There is **no shared dependency file, virtualenv, or build system across the repo.** Each recipe folder is self-contained:

- Its own `requirements.txt` listing only what that recipe needs.
- Its own `.env.example` where API keys/config are needed — copy to `.env` and fill in before running.
- No root-level `pyproject.toml` or `uv.lock` is committed (both are gitignored); `uv` is the preferred tool for ad hoc dependency management (see `tools/uv-guide/`), but `pip install -r requirements.txt` works too.

Typical workflow for a given recipe:

```bash
cd techniques/<recipe>/
pip install -r requirements.txt
cp .env.example .env   # fill in the required API key(s)
python <n-script-name>.py
```

There are no automated tests, linter config, or CI in this repo — verify changes by running the relevant script(s) directly.

## Conventions

- Python 3.12 (see `.python-version`).
- Recipes favor plain, readable scripts over frameworks-within-frameworks — e.g. `techniques/agentic-rag` builds tools (`list_files`, `grep`, `read_file`) from scratch rather than reaching for a pre-built agent toolkit, and its numbered files show the same agent implemented step-by-step, with comments noting the equivalent code in a second framework (LangChain vs. Pydantic AI) for comparison.
- Several MCP and model recipes were adapted from external courses/tutorials; their READMEs link back to the source material — preserve those attributions when editing.
- `.env` files and API keys are never committed (`.env` is gitignored); only commit `.env.example` with placeholder values.
