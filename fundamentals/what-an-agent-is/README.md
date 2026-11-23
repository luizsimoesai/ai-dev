# What an agent is

One trip request, answered twice: "Find me a one-way flight from Lisbon to Rome
on 2026-12-12 for at most 150 dollars. I can fly one day earlier or later if
needed."

- **As a chatbot** (`1-chatbot.py`): one call, no tools. The model can only
  use what it learned in training; it cannot see any flight.
- **As an agent** (`2-agent.py`): a loop. At each step the model gets the
  request and every observation so far, and proposes one action as JSON:
  `search_flights(origin, destination, date)` or `answer(text)`. The code
  checks the reply, runs the search and sends the result back as an
  observation. The loop stops at an answer or after 5 steps.

The environment is `trip.py`: fictional flights (made-up flight numbers and
prices in US dollars) from Lisbon (LIS) to Rome (FCO). No flight on 2026-12-12
fits the budget, none on 2026-12-11 does either, and one on 2026-12-13 does, so
the agent has to look at a result and decide again. The search is read-only:
nothing books a flight.

| File | What it shows |
|---|---|
| `trip.py` | The request, the flights, the `search_flights` tool (airport or city codes, like `ROM` for Rome), the JSON Schema of an action and `check()`, which validates the model's reply before anything runs. |
| `1-chatbot.py` | `anthropic/claude-haiku-5.5` and `openai/gpt-6-luna` via OpenRouter, one call each, reasoning off. Saves `results/chatbot.json`. |
| `2-agent.py` | The same two models in the perceive → decide → act → observe loop, reasoning off, with `response_format` set to a strict JSON Schema and `provider.require_parameters`. Saves `results/agent.json` after every call; if the run stops, running it again replays the saved steps and continues. |

## What the code checks

The model's reply is only text, even with a strict schema. `check()` blocks it,
and sends the error back as an observation, when:

- it is not exactly one JSON object (for example, several actions in one reply);
- it does not have exactly the fields of the schema;
- origin or destination is not a 3-letter code;
- the date is outside the three dates the user allowed (2026-12-11 to 2026-12-13).

The action is JSON in the reply, not native tool calling: the point is the
loop, not the tool-calling API.

## Run

```bash
cd fundamentals/what-an-agent-is/
cp .env.example .env            # add your OpenRouter key
uv run --with-requirements requirements.txt 1-chatbot.py
uv run --with-requirements requirements.txt 2-agent.py
```

To run them again from scratch, delete `results/`. The saved results are from
2026-11-23: 2 calls for `1-chatbot.py` and 6 for `2-agent.py`, US$ 0.0007 in
total. The answers change from run to run.

**Without OpenRouter** (not tested here): the scripts use the `openai` SDK, so
another OpenAI-compatible API needs a different `base_url`, key and model name
in `trip.py`, and the OpenRouter-only fields in `extra_body` (`reasoning`,
`provider`) removed or replaced by that API's own setting. That applies to the
OpenAI API, the Anthropic API (through its OpenAI-compatible endpoint, which
may not enforce the strict schema) and Ollama on your computer
(`http://localhost:11434/v1`, with a model that supports structured output,
such as `qwen3:8b`).
