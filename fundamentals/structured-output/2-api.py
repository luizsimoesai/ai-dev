"""
2. Asking for JSON vs a strict JSON Schema (API models)
=======================================================

The ten statement excerpts of 1-local.py, once each, on
anthropic/claude-haiku-5.5 and openai/gpt-6-luna via OpenRouter, two ways:

- prompt only: the prompt asks for JSON in a given shape;
- strict schema: response_format with the JSON Schema and "strict": True, and
  provider.require_parameters so OpenRouter only routes to a provider that
  supports it.

Reasoning is set explicitly (off here: the model only extracts; the code checks).

    uv run --with-requirements requirements.txt 2-api.py   # needs OPENROUTER_API_KEY in .env

Saves results/api.json after every call; if the run stops, running it again
skips the calls already saved. Each call records its id and cost.
"""

import json
import os
from datetime import date

from dotenv import load_dotenv
from openai import OpenAI

from statement import HERE, SAMPLES, SCHEMA, prompt, summary

MODELS = ["anthropic/claude-haiku-5.5", "openai/gpt-6-luna"]
REASONING = False
SETTINGS = {
    "prompt only": {},
    "strict schema": {"response_format": {"type": "json_schema",
                                          "json_schema": {"name": "transactions", "strict": True, "schema": SCHEMA}}},
}

load_dotenv(HERE / ".env")
api = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
RESULTS = HERE / "results" / "api.json"
saved = json.loads(RESULTS.read_text()) if RESULTS.exists() else {"date": date.today().isoformat(), "reasoning": REASONING, "calls": []}
done = {(c["model"], c["setting"], c["sample"]) for c in saved["calls"]}

for model in MODELS:
    for setting, extra in SETTINGS.items():
        for i, rows in enumerate(SAMPLES):
            if (model, setting, i) in done:
                continue
            body = {"reasoning": {"enabled": REASONING}}
            if extra:
                body["provider"] = {"require_parameters": True}
            resp = api.chat.completions.create(model=model, max_tokens=2000, **extra, extra_body=body,
                                               messages=[{"role": "user", "content": prompt(rows)}])
            saved["calls"].append({"id": resp.id, "model": model, "setting": setting, "sample": i,
                                   "text": (resp.choices[0].message.content or "").strip(),
                                   "input_tokens": resp.usage.prompt_tokens, "output_tokens": resp.usage.completion_tokens,
                                   "cost": resp.usage.model_extra["cost"], "date": date.today().isoformat()})
            RESULTS.write_text(json.dumps(saved, indent=2))  # save after every call

print(f"Reasoning {'on' if REASONING else 'off'} ({saved['date']}), {len(SAMPLES)} statement excerpts, {sum(map(len, SAMPLES))} rows")
for model in MODELS:
    for setting in SETTINGS:
        calls = sorted((c for c in saved["calls"] if c["model"] == model and c["setting"] == setting), key=lambda c: c["sample"])
        print(f"\n{model}, {setting}")
        for line in summary([{"rows": SAMPLES[c["sample"]], "text": c["text"]} for c in calls]):
            print("  " + line)
print(f"\nTotal cost: US$ {sum(c['cost'] for c in saved['calls']):.4f}")
