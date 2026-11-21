# The context window

A long supply contract and two questions: find one fact (the notice period,
in a single clause) and count the clauses that carry a penalty (spread all
over the contract). These scripts show what fits in a model's context window,
what happens to each kind of question as the contract grows, and why new text
should go at the end of the context. The contract is synthetic: every clause,
name and amount is made up.

Models: `Qwen/Qwen2.5-0.5B-Instruct` (local) and, via
[OpenRouter](https://openrouter.ai), `anthropic/claude-haiku-5.5` and
`openai/gpt-6-luna`. Prices, providers and results change over time, so every
result records its date.

| File | What it shows |
|---|---|
| `contract.py` | Builds a contract of N clauses with a fixed seed and computes the expected answers. Models, questions and the API client. |
| `0-limits.py` | Context window and longest answer of each API model, from OpenRouter's public model list. No API key. |
| `1-local-limit.py` | The local model's context limit, and both questions on contracts of 10 to 480 clauses (up to about 30,000 tokens). No API key; the first run downloads about 1 GB. Saves `results/local-limit.json`. |
| `2-long-context.py` | Both questions on the two API models, with contracts of 40, 480 and 1,600 clauses (3 runs each) and 4,800 clauses (1 run, up to about 470,000 tokens). Reports tokens, answers, the cost the API reports and the time. Saves `results/long-context.json` after every call and, if stopped, resumes from there. |
| `rebuild_from_log.py` | How the 2026-11-21 results were saved: that run stopped at call 39 of 40 (out of credit) while the script still saved only at the end, so this rebuilds the first 38 calls from the run log (answers, cost, time; no token counts). `2-long-context.py` then ran the last 2 calls. |
| `3-cache-order.py` | An amendment added after the contract reuses the provider cache; the same amendment placed before the contract does not. Shows cached tokens and cost per call. |

## Run

```bash
cd fundamentals/context-window/
cp .env.example .env            # add your OpenRouter key (scripts 2 and 3)
uv run --with-requirements requirements.txt 0-limits.py
uv run --with-requirements requirements.txt 1-local-limit.py
uv run --with-requirements requirements.txt 2-long-context.py
uv run --with-requirements requirements.txt 3-cache-order.py
```

`2-long-context.py` is the expensive one: US$ 1.24 on 2026-11-21, because both
models charge more per token above a prompt size (see
`fundamentals/cost-and-latency/0-prices.py`). Luna's repeated calls read the
contract from the provider cache, so they cost less than the first one. `3-cache-order.py` costs less
than one cent.

## Notes

- Fitting in the window is not the same as using it well. Finding one fact
  held up at every size; counting across the whole contract got worse as it
  grew.
- Anthropic models only cache the part of the request marked with
  `cache_control`; OpenAI models cache a repeated prefix on their own.
- `3-cache-order.py` puts a random reference line at the top of the contract,
  so every run starts with an empty cache.
