# Hallucination and grounding

An assistant that answers questions about a product manual. The product is
fictional (the "Brisa D-300" dehumidifier), so no model can know it from
training: anything not in the manual was made up. Five questions are answered
by the manual and three are not. Every answer is labeled in code against the
manual (see `manual.py`), and a narrow extra check lists any number in the
answer that does not appear in the manual.

Three settings: without the manual; with the manual and a rule ("if the
manual doesn't say, reply: The manual does not cover this."); and with the
manual, the rule and one example of each behavior.

| File | What it shows |
|---|---|
| `manual.py` | The manual, the eight questions, the three settings and the grading. |
| `1-local.py` | Qwen2.5-0.5B-Instruct on your computer, greedy decoding, one run per setting. No API key; the first run downloads about 1 GB. Saves `results/local.json`. |
| `2-api.py` | The same test once on `anthropic/claude-haiku-5.5` and `openai/gpt-6-luna` via OpenRouter, with reasoning set explicitly (`--reasoning on` or `off`). Saves `results/api-reasoning-<on/off>.json` after every call, resumes if stopped, records each call's id, and grades the saved answers with the current rules. |

## Run

```bash
cd fundamentals/grounding/
uv run --with-requirements requirements.txt 1-local.py
cp .env.example .env            # add your OpenRouter key (2-api.py only)
uv run --with-requirements requirements.txt 2-api.py --reasoning on
```

`2-api.py --reasoning on` cost US$ 0.0042 on 2026-11-21 (48 calls).

## Notes

- The grading is a set of simple rules for these eight questions. Read the
  answers in the results files too: a rule can miss a wording.
- Without the manual, an answer that matches it is a lucky match (a typical
  value for this kind of product), not grounding.
