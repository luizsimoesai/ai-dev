### Introduction

Personal collection of small, working AI examples, organized by concept rather than by provider or framework so the code stays easy to adapt.

## Structure

- `models/` — direct usage of each provider (OpenAI, Anthropic, Ollama): what actually changes from SDK to SDK.
- `techniques/` — provider-agnostic techniques, like RAG from scratch, agentic RAG, prompt engineering, a ReAct agent built from scratch, and typed classification.
- `fundamentals/` — embeddings, document parsing, vector databases, and NLP fundamentals.
- `mcp/` — Model Context Protocol recipes: server, client, and function-calling comparisons.
- `tools/` — supporting tooling: uv, deployment (Docker, Google Cloud), scraping, Python utilities.
- `_archive/` — content outside the scope of AI recipes (general Python/dev tutorials, third-party course copies), kept for reference.

Each code recipe carries its own `requirements.txt` (and `.env.example` where relevant) — no shared dependency file across recipes.
