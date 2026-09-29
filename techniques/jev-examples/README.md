## Jev Examples

Typed, validated classification of free text into structured judgments — a yes/no
probability, a category with confidence, or an ordinal score — using TypeSafe's Jev
"System One" model instead of hand-rolled prompts and output parsing.

Two ways to call it are shown side by side:

- The numbered files use `typesafe-sdk` directly — no LangChain involved.
- The `lc_`-prefixed files use `langchain-typesafe`, a LangChain `Runnable` wrapper
  around the same API, plus two experimental agent middlewares built on top of it.

### Requirements

- Python 3.12+
- A TypeSafe API key (`TYPESAFE_API_KEY`)
- An OpenAI API key (`OPENAI_API_KEY`) — only for `lc_auto_mode_example.py` and
  `lc_model_router_example.py`

### Usage

```bash
pip install -r requirements.txt
cp .env.example .env  # add your TYPESAFE_API_KEY (and OPENAI_API_KEY for the lc_ agent examples)
python 1-noul.py
```

### Contents

Numbered, jev-native (`typesafe_sdk`, no LangChain) — from simplest to most complex:

- `1-noul.py` — binary question: returns the probability of "yes" for a question (e.g. "is this urgent?").
- `2-choice.py` — categorical question: picks a label among fixed alternatives, with per-label probability and confidence (e.g. routing to a team).
- `3-score.py` — ordinal question: rates the state against an ordered rubric, returning a (possibly fractional) score and the probability distribution over levels.
- `4-combined.py` — combines `Choice`, `Noul`, and `Score` in a single call, answering several questions about the same state at once.
- `5-async.py` — same flow as `1-noul.py`, using `AsyncTypeSafeClient` and `await client.system_one(...)`.

LangChain integration (`langchain_typesafe`), same primitives via `TypeSafeClassifier.invoke`/`ainvoke`:

- `lc_noul_example.py`, `lc_choice_example.py`, `lc_score_example.py`, `lc_combined_example.py`, `lc_async_example.py` — mirror the numbered examples above through the LangChain `Runnable` interface.
- `lc_auto_mode_example.py` — `AutoModeMiddleware`: plugged into a LangChain agent, automatically blocks tool calls classified as risky before they run.
- `lc_model_router_example.py` — `ModelRouterMiddleware`: classifies the user's task and routes the agent call to the most suitable model (fast vs. powerful).

`lc_auto_mode_example.py` and `lc_model_router_example.py` are experimental and require LangChain's agent support (`langchain.agents.create_agent`).
