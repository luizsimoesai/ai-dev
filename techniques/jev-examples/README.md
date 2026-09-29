## Jev Examples

Typed, validated classification of free text into structured judgments — a yes/no
probability, a category with confidence, or an ordinal score — using
`langchain-typesafe` instead of hand-rolled prompts and output parsing. Also includes
two experimental agent middlewares built on top of it: one that blocks risky tool calls
pending confirmation, another that routes each request to the cheapest model able to
handle it.

### Requirements

- Python 3.12+
- A TypeSafe API key (`TYPESAFE_API_KEY`)
- An OpenAI API key (`OPENAI_API_KEY`) — only for the agent middleware examples

### Usage

```bash
pip install -r requirements.txt
cp .env.example .env  # add your TYPESAFE_API_KEY (and OPENAI_API_KEY for the agent examples)
python noul_example.py
```

### Contents

From simplest to most complex:

- `noul_example.py` — binary question: returns the probability of "yes" for a question (e.g. "is this urgent?").
- `choice_example.py` — categorical question: picks a label among fixed alternatives, with per-label probability and confidence (e.g. routing to a team).
- `score_example.py` — ordinal question: rates the state against an ordered rubric, returning a (possibly fractional) score and the probability distribution over levels.
- `combined_example.py` — combines `Choice`, `Noul`, and `Score` in a single call, answering several questions about the same state at once.
- `async_example.py` — same flow as `noul_example.py`, using `ainvoke` asynchronously.
- `auto_mode_example.py` — `AutoModeMiddleware`: plugged into a LangChain agent, automatically blocks tool calls classified as risky before they run.
- `model_router_example.py` — `ModelRouterMiddleware`: classifies the user's task and routes the agent call to the most suitable model (fast vs. powerful).

`auto_mode_example.py` and `model_router_example.py` are experimental and require LangChain's agent support (`langchain.agents.create_agent`).
