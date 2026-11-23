# Start simple

One request, three ways to build it: plain code, one LLM call and an agent.
The request is "Adjust the pancake recipe for 6 people."

The recipe (`recipe.py`) is fictional: pancakes for 4, in metric units. Every
quantity scales to an exact number except one: 3 eggs for 4 people become 4.5
for 6. The app's rule, written in `scale()`, is that eggs are counted whole and
rounded up, so the app's answer is 5 eggs. The requests sent to the models do
not mention that rule, as in a real app where the rule lives in the code.

| File | What it shows |
|---|---|
| `recipe.py` | The recipe, the `scale()` function with the rule for whole items, the check (`check()`: every ingredient as `scale()` returns it, same name and unit), the two tools for the agent and the saved results. |
| `1-function.py` | No LLM: `scale()` multiplies every quantity and applies the rule. No API key needed. |
| `2-one-call.py` | One call per model: the recipe as JSON and the request go in, the scaled ingredients come back with a strict JSON Schema, and the code checks them. Saves `results/one-call.json`. |
| `3-agent.py` | The loop of `fundamentals/what-an-agent-is` with two tools, `get_recipe` and `scale_recipe` (the `scale()` function itself): at each step the model picks one JSON action, the code checks it and runs it, and the result goes back as an observation. At most 6 steps. Saves `results/agent.json` after every call; if the run stops, running it again replays the saved steps and continues. |

Both LLM scripts use `anthropic/claude-haiku-5.5` and `openai/gpt-6-luna` via
OpenRouter, with reasoning off and `provider.require_parameters`, so the
strict schema is enforced.

## Run

```bash
cd fundamentals/start-simple/
uv run --with-requirements requirements.txt 1-function.py
cp .env.example .env            # add your OpenRouter key
uv run --with-requirements requirements.txt 2-one-call.py
uv run --with-requirements requirements.txt 3-agent.py
```

To run the LLM scripts again from scratch, delete `results/`. The saved results
are from 2026-11-23: 2 calls for `2-one-call.py` and 6 for `3-agent.py`,
US$ 0.0008 in total. The answers and the agent's steps can change from run to
run.

**Without OpenRouter** (not tested here): the scripts use the `openai` SDK, so
another OpenAI-compatible API needs a different `base_url`, key and model name
in `recipe.py`, and the OpenRouter-only fields in `extra_body` (`reasoning`,
`provider`) removed or replaced by that API's own setting. That applies to the
OpenAI API, the Anthropic API (through its OpenAI-compatible endpoint, which
may not enforce the strict schema) and Ollama on your computer
(`http://localhost:11434/v1`, with a model that supports structured output,
such as `qwen3:8b`).
