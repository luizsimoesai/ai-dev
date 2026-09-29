# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal collection of small, working AI/LLM example scripts and notebooks, organized by **concept** rather than by provider or framework, so code stays easy to adapt and compare. This is not a single application — there is no shared entry point, build, or test suite across the repo.

## Repository layout

- `models/` — direct usage of each provider SDK: `openai_api/`, `anthropic_api/`, `ollama_api/` — what actually differs from SDK to SDK.
- `techniques/` — provider-agnostic techniques: RAG from scratch, agentic RAG, prompt engineering, a ReAct agent built from scratch, typed classification, etc.
- `fundamentals/` — embeddings, document parsing, vector databases, NLP fundamentals.
- `mcp_protocol/` — Model Context Protocol recipes: server setup, client usage, function-calling comparisons, Docker packaging.
- `tools/` — supporting tooling: uv, deployment (Docker, Google Cloud), scraping (Firecrawl), Python utilities.
- `_archive/` — content outside the scope of AI recipes (general Python/dev tutorials, third-party course copies), kept for reference only — do not treat as active code.

Each numbered recipe directory (e.g. `techniques/agentic-rag/1-build-tools.py`, `2-import-tools.py`, ...) is a progressive walkthrough: later files build on earlier ones and often import shared helpers from a local `utils/` subfolder. Read the recipe's own `README.md` before editing — it documents what each numbered file demonstrates.

## Running code

There is **no shared dependency file, virtualenv, or build system across the repo.** Each recipe folder is self-contained:

- Its own `requirements.txt` listing only what that recipe needs.
- Its own `.env.example` where API keys/config are needed — copy to `.env` and fill in before running.
- No `pyproject.toml` or `uv.lock` is committed anywhere in the repo (both are gitignored, at any depth) — `requirements.txt` is the committed source of truth for a recipe's dependencies.

Preferred workflow: `uv`, with its own `pyproject.toml`/`uv.lock`/`.venv` scaffolded per recipe folder (mirrors the per-folder `requirements.txt` isolation). From the recipe folder:

```bash
cd techniques/<recipe>/
uv init --bare                 # scaffolds pyproject.toml (no README/git init/.python-version — repo already has those)
uv add -r requirements.txt     # imports deps into pyproject.toml, creates .venv/ and uv.lock
cp .env.example .env           # fill in the required API key(s), if any
uv run <n-script-name>.py      # runs inside the recipe's own environment, no manual activation
```

Only run `uv init --bare` once per folder (skip it if `pyproject.toml` is already there from a previous session). If you add a new dependency mid-task, use `uv add <package>` (not a manual `requirements.txt` edit) so `pyproject.toml`/`uv.lock` stay authoritative — then update `requirements.txt` to match before committing, since that's the file other people (without `uv`) will install from.

`uv init --bare` names the project after the current folder. Folders were renamed (`openai_api/`, `anthropic_api/`, `ollama_api/`, `mcp_protocol/`) precisely so that name never collides with a same-named dependency in that folder's `requirements.txt` — `uv add` refuses to add a package that matches the project's own name (a self-dependency). If you ever create a new recipe folder whose name matches one of its own dependencies, either name the folder to avoid the collision or pass `uv init --bare --name <something-else>`.

`pip install -r requirements.txt` + a manually-activated venv also works if `uv` isn't available.

There are no automated tests, linter config, or CI in this repo — verify changes by running the relevant script(s) directly.

## Conventions

- Python 3.12 (see `.python-version`).
- Recipes favor plain, readable scripts over frameworks-within-frameworks — e.g. `techniques/agentic-rag` builds tools (`list_files`, `grep`, `read_file`) from scratch rather than reaching for a pre-built agent toolkit, and its numbered files show the same agent implemented step-by-step, with comments noting the equivalent code in a second framework (LangChain vs. Pydantic AI) for comparison.
- Several MCP and model recipes were adapted from external courses/tutorials; their READMEs link back to the source material — preserve those attributions when editing.
- `.env` files and API keys are never committed (`.env` is gitignored); only commit `.env.example` with placeholder values.
