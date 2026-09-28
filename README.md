### Introduction

This repository is a collection of practical, copy/paste-ready recipes for building AI systems — organized by concept, not by provider or framework, so the code stays easy to adapt regardless of which SDK or library you're using.

## Structure

- `models/` — direct usage of each provider (OpenAI, Anthropic, Ollama): what actually changes from SDK to SDK.
- `patterns/` — provider-agnostic patterns, like RAG from scratch and prompt engineering.
- `knowledge/` — embeddings, document parsing, vector databases, and NLP fundamentals.
- `mcp/` — Model Context Protocol recipes: server, client, and function-calling comparisons.
- `tools/` — supporting tooling: uv, deployment (Docker, Google Cloud), scraping, Python utilities.
- `_archive/` — content outside the scope of AI recipes (general Python/dev tutorials, third-party course copies), kept for reference.

Each leaf folder carries its own `requirements.txt` (and `.env.example` where relevant) — no shared dependency file across recipes.
