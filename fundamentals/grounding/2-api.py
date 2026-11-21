"""
2. The same test on two API models
==================================

The eight questions and three settings of 1-local.py, once each, on
anthropic/claude-haiku-5.5 and openai/gpt-6-luna via OpenRouter. Reasoning is
set explicitly, never left to the provider's default:

    uv run 2-api.py --reasoning on     # needs OPENROUTER_API_KEY in .env
    uv run 2-api.py --reasoning off

Saves results/api-reasoning-<on|off>.json after every call; if the run stops,
running it again skips the calls already saved. Each call records its id.
"""

import argparse
import json
import os
from collections import Counter
from datetime import date

from dotenv import load_dotenv
from openai import OpenAI

from manual import HERE, QUESTIONS, SETTINGS, label, messages, numbers_not_in_manual

MODELS = ["anthropic/claude-haiku-5.5", "openai/gpt-6-luna"]
parser = argparse.ArgumentParser()
parser.add_argument("--reasoning", choices=["on", "off"], required=True)
REASONING = parser.parse_args().reasoning == "on"

load_dotenv(HERE / ".env")
api = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
RESULTS = HERE / "results" / f"api-reasoning-{'on' if REASONING else 'off'}.json"
saved = json.loads(RESULTS.read_text()) if RESULTS.exists() else {"date": date.today().isoformat(), "reasoning": REASONING, "rows": []}
done = {(r["model"], r["setting"], r["question"]) for r in saved["rows"]}

for model in MODELS:
    for setting in SETTINGS:
        for question, check in QUESTIONS:
            if (model, setting, question) in done:
                continue
            resp = api.chat.completions.create(model=model, max_tokens=4000, messages=messages(setting, question),
                                               extra_body={"reasoning": {"enabled": REASONING}})
            answer = (resp.choices[0].message.content or "").strip().replace("\n", " ")
            u = resp.usage
            saved["rows"].append({"id": resp.id, "model": model, "setting": setting, "question": question,
                                  "label": label(check, answer, setting != "no manual"), "numbers_not_in_manual": numbers_not_in_manual(answer),
                                  "answer": answer, "input_tokens": u.prompt_tokens, "output_tokens": u.completion_tokens,
                                  "cost": u.model_extra["cost"], "date": date.today().isoformat()})
            RESULTS.write_text(json.dumps(saved, indent=2))  # save after every call

checks = dict(QUESTIONS)
for r in saved["rows"]:  # grade the saved answers with the current rules (no new calls)
    r["label"] = label(checks[r["question"]], r["answer"], r["setting"] != "no manual")
    r["numbers_not_in_manual"] = numbers_not_in_manual(r["answer"])
RESULTS.write_text(json.dumps(saved, indent=2))

print(f"Reasoning {'on' if REASONING else 'off'} ({saved['date']})")
for model in MODELS:
    for setting in SETTINGS:
        rows = [r for r in saved["rows"] if r["model"] == model and r["setting"] == setting]
        print(f"\n{model}, {setting}")
        for r in rows:
            flag = f"  [numbers not in manual: {', '.join(r['numbers_not_in_manual'])}]" if r["numbers_not_in_manual"] else ""
            print(f"  {r['question']:<43} {r['label']:<21} {r['answer'][:70]}{flag}")
        print("  " + ", ".join(f"{k}: {v}" for k, v in Counter(r["label"] for r in rows).items()))
print(f"\nTotal cost: US$ {sum(r['cost'] for r in saved['rows']):.4f}")
