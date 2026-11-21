# Structured output

An app turns a pasted bank statement into transactions that code can sum and
filter. Ten short excerpts of a synthetic statement (`statement.csv`, made-up
merchants and amounts in US dollars) are rendered as plain text, and a model
extracts every transaction as JSON: date, description, amount and one category
from a fixed list. Each answer is checked three ways:

- **format**: is it JSON, and does it follow the schema?
- **answer key**: date, amount and category of every row, against the CSV;
- **code check**: what code can verify from the statement text alone, with no
  model and no answer key (one transaction per dated line; every amount, with
  its sign, appears in the text).

| File | What it shows |
|---|---|
| `statement.py` | The excerpts, the prompt, the JSON Schema and the checks. |
| `1-local.py` | Qwen2.5-0.5B-Instruct on your computer: asking for JSON in the prompt vs a minimal constrained decoder, where the code writes the fixed parts of the JSON and the model only fills the fields, token by token, among the tokens that fit. No API key; the first run downloads about 1 GB and takes a few minutes. Saves `results/local.json`. |
| `2-api.py` | `anthropic/claude-haiku-5.5` and `openai/gpt-6-luna` via OpenRouter, reasoning off: asking for JSON in the prompt vs `response_format` with a strict JSON Schema (and `provider.require_parameters`). Saves `results/api.json` after every call and resumes if stopped. |

## Run

```bash
cd fundamentals/structured-output/
uv run --with-requirements requirements.txt 1-local.py
cp .env.example .env            # add your OpenRouter key (2-api.py only)
uv run --with-requirements requirements.txt 2-api.py
```

`2-api.py` cost US$ 0.0050 on 2026-11-21 (40 calls).

## Notes

- The constrained decoder in `1-local.py` is written to show the idea and
  recomputes the whole sequence at every step, so it is slower than plain
  generation. Libraries such as SGLang, Outlines or llguidance do it fast.
- Where the fixed text ends matters: if it ends with a space (`"amount": `),
  the model can't use its usual token for " -2" and tends to drop the sign.
  The decoder leaves that space to the model.
- A valid answer can still be wrong: format is guaranteed, content is not.
