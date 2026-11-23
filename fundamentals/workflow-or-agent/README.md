# Workflow or agent

One handbook assistant, built twice. The only difference is who decides the
next step: the code (workflow) or the model (agent).

The handbook (`handbook.py`) is fictional: four short policy documents, with
amounts in US dollars. Three questions:

| Question | Where the answer is | A right answer contains |
|---|---|---|
| `flight-booking` | `travel` | `14` (days) |
| `coworking-abroad` | split: `remote-work` says coworking is reimbursed "under the expenses policy"; the cap is only in `expenses` | `300` (dollars) and the manager's approval |
| `parental-leave` | nowhere | the fixed reply `The handbook does not cover this.` |

The checks are in `is_right()` in `handbook.py`. They look for the facts a
right answer must contain; they do not check that the rest of the answer is
true.

| File | What it shows |
|---|---|
| `handbook.py` | The documents, the questions, the checks, the two read-only tools (`list_documents`, `read_document`) and the saved results. |
| `1-workflow.py` | The code decides every step: match the question's words with each document's topics; a gate that stops with the fixed reply, without an LLM call, when nothing matches; read the one best-matching document; one LLM call drafts the answer. Saves `results/workflow.json`. |
| `2-agent.py` | The loop of `fundamentals/what-an-agent-is` with the two document tools: at each step the model picks one JSON action (`list_documents`, `read_document` or `answer`), the code checks it and runs it, and the result goes back as an observation. At most 6 steps. Saves `results/agent.json` after every call; if the run stops, running it again replays the saved steps and continues. |

Both use `anthropic/claude-haiku-5.5` and `openai/gpt-6-luna` via OpenRouter,
with reasoning off. The agent asks for a strict JSON Schema with
`provider.require_parameters`; the reply is still checked in code, because it
can still be several JSON objects in one reply.

The workflow reads one document by design, so it cannot follow the reference
from `remote-work` to `expenses`. If that case is known in advance, one more
step in the code (read the documents a document refers to) covers it, still
with one LLM call.

## Run

```bash
cd fundamentals/workflow-or-agent/
cp .env.example .env            # add your OpenRouter key
uv run --with-requirements requirements.txt 1-workflow.py
uv run --with-requirements requirements.txt 2-agent.py
```

To run them again from scratch, delete `results/`. The saved results are from
2026-11-23: 4 calls for `1-workflow.py` and 20 for `2-agent.py`, US$ 0.0014 in
total. The answers and the agent's steps change from run to run.

**Without OpenRouter** (not tested here): the scripts use the `openai` SDK, so
another OpenAI-compatible API needs a different `base_url`, key and model name
in `handbook.py`, and the OpenRouter-only fields in `extra_body` (`reasoning`,
`provider`) removed or replaced by that API's own setting. That applies to the
OpenAI API, the Anthropic API (through its OpenAI-compatible endpoint, which
may not enforce the strict schema) and Ollama on your computer
(`http://localhost:11434/v1`, with a model that supports structured output,
such as `qwen3:8b`).
