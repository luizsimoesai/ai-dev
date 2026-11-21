"""
2. Where the time and the money go: reasoning, answer, first token
==================================================================

Both models reason before they answer, by default. The reasoning tokens are
billed as output tokens, and they come out before the first token of the
answer, so they also add to the wait. This script streams one question and
compares three settings:
  - reasoning on, the answer shows the work (the default in 1-accuracy.py);
  - reasoning on, number only;
  - reasoning off, number only.
For each one it times the first token of the ANSWER (not of the reasoning) and
the whole call, counts reasoning and answer tokens, reads the cost and grades
the answer. Two models, two statement sizes, three runs each: 36 calls.

    uv run 2-latency.py           # needs OPENROUTER_API_KEY in .env
"""

import json
import re
import time
from datetime import date
from statistics import median

from common import HERE, MODELS, STATEMENTS, client, load, messages, questions

RUNS = 3
NUMBER_ONLY = " Reply with the FINAL ANSWER line only, nothing else."
SETTINGS = {
    "reasoning, shows work": ("", {}),
    "reasoning, number only": (NUMBER_ONLY, {}),
    "no reasoning, number": (NUMBER_ONLY, {"reasoning": {"enabled": False}}),
}
api = client()


def timed(model: str, msgs: list[dict], extra: dict) -> dict:
    start = time.perf_counter()
    first_answer, usage, provider, text = None, None, None, ""
    stream = api.chat.completions.create(model=model, messages=msgs, max_tokens=4000, stream=True,
                                         stream_options={"include_usage": True}, extra_body=extra)
    for chunk in stream:
        provider = provider or (chunk.model_extra or {}).get("provider")
        if chunk.choices and chunk.choices[0].delta.content:
            if first_answer is None:
                first_answer = time.perf_counter() - start  # first token of the answer itself
            text += chunk.choices[0].delta.content
        if chunk.usage:
            usage = chunk.usage
    reasoning = (usage.completion_tokens_details.reasoning_tokens or 0) if usage.completion_tokens_details else 0
    found = re.findall(r"FINAL ANSWER:\s*\$?\s*(-?[\d,]*\.?\d+)", text)
    return {"first_answer_s": first_answer, "total_s": time.perf_counter() - start,
            "input_tokens": usage.prompt_tokens, "reasoning_tokens": reasoning,
            "answer_tokens": usage.completion_tokens - reasoning,
            "cost": (usage.model_extra or {}).get("cost"), "provider": provider,
            "answer": float(found[-1].replace(",", "")) if found else None}


today = date.today().isoformat()
results = []
print(f"Median of {RUNS} runs ({today}). Question: how much did I spend on groceries in October 2026?\n")
print(f"{'model':<27}{'stmt':<6}{'setting':<24}{'in tok':>7}{'reason':>7}{'answer':>7}"
      f"{'1st ans s':>10}{'total s':>8}{'US$/call':>10}{'right':>6}")
for size, file in STATEMENTS.items():
    csv_text, rows = load(file)
    q = questions(rows)[0]
    for model in MODELS:
        for setting, (suffix, extra) in SETTINGS.items():
            runs = [timed(model, messages(csv_text, q["question"] + suffix), extra) for _ in range(RUNS)]
            right = sum(r["answer"] is not None and abs(r["answer"] - q["expected"]) <= 0.01 for r in runs)
            results.append({"model": model, "statement": size, "setting": setting, "expected": q["expected"],
                            "right": right, "runs": runs})
            m = lambda k: median(r[k] for r in runs)
            print(f"{model:<27}{size.split()[0] + 'm':<6}{setting:<24}{m('input_tokens'):>7,.0f}"
                  f"{m('reasoning_tokens'):>7,.0f}{m('answer_tokens'):>7,.0f}{m('first_answer_s'):>10.1f}"
                  f"{m('total_s'):>8.1f}{m('cost'):>10.5f}{right:>4}/{RUNS}")
(HERE / "results" / "latency.json").write_text(json.dumps({"date": today, "results": results}, indent=2))
wrong = sorted({r["answer"] for x in results if x["setting"].startswith("no") for r in x["runs"]
                if r["answer"] is not None and abs(r["answer"] - x["expected"]) > 0.01})
print(f"\nWrong answers without reasoning: {wrong}")
print("Providers used:", sorted({r["provider"] for x in results for r in x["runs"] if r["provider"]}))
