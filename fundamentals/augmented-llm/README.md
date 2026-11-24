# The augmented LLM

One LLM call, extended three ways: retrieval and memory put information into
the request; a tool lets the model ask for an action that the code runs.

The codebase is fictional: `project/` is **shortlinks**, a small link shortener
with three modules (`slugs.py`, `store.py`, `expiry.py`) and six tests. One
test fails on purpose: `is_expired()` uses `>` where
`test_link_expires_on_day_90` expects a link to expire on day 90.

| File | What it shows |
|---|---|
| `assistant.py` | The models, one LLM call with a strict JSON Schema, the saved results and the project files. |
| `1-retrieval.py` | "What is the maximum length of a custom slug, and which function checks it?" Without retrieval, and with a keyword search: the code ranks the project files by how many words of the question they contain and puts the top 2 in the request; it also prints the input tokens of each call. Saves `results/retrieval.json`. |
| `2-tool.py` | "Do the shortlinks tests pass? If not, which test fails?" Without a tool, and with the read-only action `run_tests`: the model replies with a JSON action, the code runs pytest and sends the summary back as an observation. At most 3 steps. Saves `results/tool.json`. |
| `3-memory.py` | Session 1: the user states a convention (new function names start with `sl_`); one call extracts what to remember and the code saves it to `results/memory.json`. Session 2, a new conversation: write a new function, without and with the saved notes in the system prompt. The code checks every function name, and counts the arguments of each call to `is_expired` (the project's `is_expired(link, now)` needs 2). Saves `results/memory-calls.json`. |

All three scripts use `anthropic/claude-haiku-5.5` and `openai/gpt-6-luna` via
OpenRouter, with reasoning off and `provider.require_parameters`, so the
strict schema is enforced. The actions are JSON replies, as in
`fundamentals/what-an-agent-is`; the APIs' native tool calling format is not
used here.

## Run

```bash
cd fundamentals/augmented-llm/
cp .env.example .env            # add your OpenRouter key
uv run --with-requirements requirements.txt 1-retrieval.py
uv run --with-requirements requirements.txt 2-tool.py
uv run --with-requirements requirements.txt 3-memory.py
```

To see the failing test yourself: `cd project && uv run --with pytest python -m pytest -q`.

To run the scripts again from scratch, delete `results/`. The saved results are
from 2026-11-24: 4 calls for `1-retrieval.py`, 6 for `2-tool.py` and 6 for
`3-memory.py`, US$ 0.0010 in total. The answers can change from run to run.

**Without OpenRouter** (not tested here): the scripts use the `openai` SDK, so
another OpenAI-compatible API needs a different `base_url`, key and model name
in `assistant.py`, and the OpenRouter-only fields in `extra_body` (`reasoning`,
`provider`) removed or replaced by that API's own setting. That applies to the
OpenAI API, the Anthropic API (through its OpenAI-compatible endpoint, which
may not enforce the strict schema) and Ollama on your computer
(`http://localhost:11434/v1`, with a model that supports structured output,
such as `qwen3:8b`).
