"""
2. The same test on two API models
==================================

The eight messages and two system prompts of cases.py, once each, on
anthropic/claude-haiku-5.5 and openai/gpt-6-luna via OpenRouter, with
reasoning off (set explicitly: a support assistant in production).

    uv run --with-requirements requirements.txt 2-api.py   # needs OPENROUTER_API_KEY in .env

Saves results/api.json after every call; if the run stops, running it again
skips the calls already saved. Each call records its id and cost.
"""

import json
import os
from datetime import date

from dotenv import load_dotenv
from openai import OpenAI

from cases import CASES, HERE, PROMPTS, messages, report

MODELS = ["anthropic/claude-haiku-5.5", "openai/gpt-6-luna"]
REASONING = False

load_dotenv(HERE / ".env")
api = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
RESULTS = HERE / "results" / "api.json"
saved = json.loads(RESULTS.read_text()) if RESULTS.exists() else {"date": date.today().isoformat(), "reasoning": REASONING, "calls": []}
done = {(c["model"], c["prompt"], c["case"]) for c in saved["calls"]}

for model in MODELS:
    for prompt in PROMPTS:
        for case in CASES:
            if (model, prompt, case) in done:
                continue
            resp = api.chat.completions.create(model=model, max_tokens=400, messages=messages(prompt, case),
                                               extra_body={"reasoning": {"enabled": REASONING}})
            saved["calls"].append({"id": resp.id, "model": model, "prompt": prompt, "case": case,
                                   "answer": (resp.choices[0].message.content or "").strip().replace("\n", " "),
                                   "input_tokens": resp.usage.prompt_tokens, "output_tokens": resp.usage.completion_tokens,
                                   "cost": resp.usage.model_extra["cost"], "date": date.today().isoformat()})
            RESULTS.write_text(json.dumps(saved, indent=2))  # save after every call

print(f"Reasoning {'on' if REASONING else 'off'} ({saved['date']})")
for model in MODELS:
    print(f"\n{model}")
    print("\n".join(report([c for c in saved["calls"] if c["model"] == model])))
print(f"\nTotal cost: US$ {sum(c['cost'] for c in saved['calls']):.4f}")
