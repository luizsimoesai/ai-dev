# Cost, latency and choosing a model

A bank-statement assistant in its simplest form: the whole statement (CSV) goes
in every question. These scripts measure what that costs, where the time goes,
and how two models from different vendors compare on the same questions. The
statements are synthetic: every name, amount and date is made up.

Models (via [OpenRouter](https://openrouter.ai)): `anthropic/claude-haiku-5.5`
and `openai/gpt-6-luna`. Prices, providers and results change over time, so
every result file records its date.

| File | What it shows |
|---|---|
| `make_statement.py` | Generates `statement-3m.csv` (199 transactions) and `statement-12m.csv` (776) with a fixed seed. No API key. |
| `0-prices.py` | Price per million tokens (input, output, cached input) and structured-output support for each provider of each model, read from OpenRouter's public endpoint list. No API key. |
| `1-accuracy.py` | 10 questions x 3 runs x 2 models x 2 statement sizes (120 calls). Grades every answer against the value computed in Python, counts the questions whose answer varied between runs, and reports tokens, cost and time per call. Question 8 is ambiguous on purpose (is a transfer to savings an expense?). Saves `results/accuracy-*.json`. With `--no-reasoning`, the same test with reasoning turned off, saved as `results/accuracy-*-no-reasoning.json` and ending with the wrong answers per question. |
| `2-latency.py` | Streams one question in three settings: reasoning on (shows work), reasoning on (number only), reasoning off (number only). Times the first token of the answer and the whole call, counts reasoning and answer tokens, reads the cost and grades the answer (36 calls). Saves `results/latency.json`. |
| `3-one-call.py` | One call per model: input, cached input, output and reasoning tokens, the cost the API reports, and the estimate from the list price. |
| `4-read-results.py` | No API calls: reads the saved accuracy results and shows, for the ambiguous question 8, which total each answer gave and whether it said which rule it used, plus the average answer length per model. |
| `5-latency-metrics.py` | No API calls: reads the saved latency results and names the two parts of the wait, TTFT (time to first token of the answer) and TPOT (time per answer token after the first), with the medians per setting and the estimate TTFT + TPOT x output tokens next to the measured total. |
| `common.py` | Models, statements, the ten questions with their expected answers, and the API client. |

## Run

```bash
cd fundamentals/cost-and-latency/
cp .env.example .env            # add your OpenRouter key
uv run --with-requirements requirements.txt 0-prices.py
uv run --with-requirements requirements.txt 1-accuracy.py
uv run --with-requirements requirements.txt 1-accuracy.py --no-reasoning
uv run --with-requirements requirements.txt 2-latency.py
uv run --with-requirements requirements.txt 3-one-call.py
uv run --with-requirements requirements.txt 4-read-results.py
uv run --with-requirements requirements.txt 5-latency-metrics.py
```

A full run of `1-accuracy.py` cost about US$ 0.15 on 2026-11-21 (US$ 0.13 with `--no-reasoning`); `2-latency.py`
and `3-one-call.py` cost a few tenths of a cent.

## Notes

- Both models reason before answering by default. Reasoning tokens are billed
  as output tokens and come out before the first token of the answer.
- The same CSV is a different number of tokens for each model (each has its own
  tokenizer), so the price per million tokens alone doesn't tell you the cost.
- Repeated input can be read from a provider cache at a lower price; whether
  that happens depends on the provider.
