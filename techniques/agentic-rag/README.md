## Agentic RAG

An agent that answers questions over a folder of markdown notes by calling search tools
(`list_files`, `grep`, `read_file`) instead of a vector database — no embeddings, no
chunking, no similarity search. The model decides what to look up and iterates until it
has enough context to answer.

Built with [LangChain](https://docs.langchain.com/oss/python/langchain/agents), running
OpenRouter-hosted models (OpenAI-compatible API). Each file's comments also show the
equivalent [Pydantic AI](https://ai.pydantic.dev/agents/) implementation the code was
ported from, so you can compare both frameworks step by step.

### Requirements

- Python 3.12+
- An [OpenRouter](https://openrouter.ai/) API key
- [ripgrep](https://github.com/BurntSushi/ripgrep) (`brew install ripgrep`) — only needed for `6-production.py`

### Usage

```bash
pip install -r requirements.txt
cp .env.example .env  # add your OPENROUTER_API_KEY
python 3-basic-agent.py
```

### Contents

- `1-build-tools.py` — builds `list_files`, `grep`, and `read_file` step by step before they move into `utils/tools.py`.
- `2-import-tools.py` — imports the finished tools and shows what each one returns.
- `3-basic-agent.py` — wires the three tools into a LangChain agent that answers a question from the notes.
- `4-streaming-steps.py` — streams the agent's intermediate tool calls as they happen.
- `5-structured-output.py` — forces the agent to answer with a validated `SearchAnswer` schema (citations included) instead of free text.
- `6-production.py` — production-hardened tools and agent: ripgrep-backed search, bounded reads, path validation, logging, and a request cap.
- `utils/tools.py` — the canonical `list_files` / `grep` / `read_file` implementations shared by files 2–5.
- `utils/streaming.py` — formats streamed tool results for display.
- `notes/` — a fictitious company's internal docs, used as the search corpus.
