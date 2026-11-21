"""
1. Accuracy, variation and cost: the whole statement in every question
======================================================================

Ten questions about a synthetic bank statement, three runs each, for two
models and two statement sizes (3 and 12 months): 120 calls, a few US cents.
The whole CSV goes in every request. Each answer ends with 'FINAL ANSWER: <n>'
and is graded against the value computed in Python.

    uv run 1-accuracy.py                  # needs OPENROUTER_API_KEY in .env
    uv run 1-accuracy.py --no-reasoning   # same test with reasoning turned off

Both models reason before answering by default. --no-reasoning sends
reasoning: {"enabled": false} and saves the results with a -no-reasoning suffix.
"""

import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date

from common import HERE, MODELS, STATEMENTS, client, load, messages, questions

RUNS = 3
MAX_TOKENS = 4000
NO_REASONING = "--no-reasoning" in sys.argv
EXTRA = {"reasoning": {"enabled": False}} if NO_REASONING else {}
SUFFIX = "-no-reasoning" if NO_REASONING else ""
api = client()


def ask(model: str, csv_text: str, question: str) -> dict:
    start = time.perf_counter()
    resp = api.chat.completions.create(model=model, max_tokens=MAX_TOKENS, messages=messages(csv_text, question),
                                      extra_body=EXTRA)
    text = resp.choices[0].message.content or ""
    found = re.findall(r"FINAL ANSWER:\s*\$?\s*(-?[\d,]*\.?\d+)", text)
    extra = resp.usage.model_extra or {}
    return {
        "answer": float(found[-1].replace(",", "")) if found else None,
        "seconds": round(time.perf_counter() - start, 1),
        "input_tokens": resp.usage.prompt_tokens,
        "reasoning_tokens": getattr(resp.usage.completion_tokens_details, "reasoning_tokens", None),
        "output_tokens": resp.usage.completion_tokens,
        "cost": extra.get("cost"),
        "provider": (resp.model_extra or {}).get("provider"),
        "finish_reason": resp.choices[0].finish_reason,
        "text": text,
    }


today = date.today().isoformat()
summary = []
for size, file in STATEMENTS.items():
    csv_text, rows = load(file)
    qs = questions(rows)
    for model in MODELS:
        jobs = [(i, run) for i in range(len(qs)) for run in range(RUNS)]
        with ThreadPoolExecutor(max_workers=6) as pool:
            out = list(pool.map(lambda j: {"q": j[0] + 1, "run": j[1] + 1, **ask(model, csv_text, qs[j[0]]["question"])}, jobs))
        for r in out:
            item = qs[r["q"] - 1]
            close = lambda v: r["answer"] is not None and v is not None and abs(r["answer"] - v) <= 0.01
            r["ok"], r["ok_alt"] = close(item["expected"]), close(item["expected"]) or close(item["alternative"])
        varied = sorted({r["q"] for r in out if len({x["answer"] for x in out if x["q"] == r["q"]}) > 1})
        n = len(out)
        s = {
            "model": model, "statement": size, "rows": len(rows), "calls": n, "reasoning": not NO_REASONING,
            "correct": sum(r["ok"] for r in out),
            "correct_accepting_q8": sum(r["ok_alt"] for r in out),
            "questions_that_varied": varied,
            "input_tokens_per_call": round(sum(r["input_tokens"] for r in out) / n),
            "output_tokens_per_call": round(sum(r["output_tokens"] for r in out) / n),
            "cost_total": round(sum(r["cost"] or 0 for r in out), 4),
            "cost_per_call": round(sum(r["cost"] or 0 for r in out) / n, 5),
            "seconds_per_call": round(sum(r["seconds"] for r in out) / n, 1),
            "providers": sorted({r["provider"] for r in out if r["provider"]}),
        }
        summary.append(s)
        (HERE / "results" / f"accuracy-{model.split('/')[1]}-{file.split('-')[1].split('.')[0]}{SUFFIX}.json").write_text(
            json.dumps({"date": today, "summary": s, "questions": qs, "runs": out}, indent=2))
        for r in out:
            if not r["ok_alt"]:
                print(f"  wrong: {model} {size} Q{r['q']} run {r['run']}: {r['answer']} (expected {qs[r['q'] - 1]['expected']})")

print(f"\nSummary ({today}, reasoning {'off' if NO_REASONING else 'on'}): {RUNS} runs x 10 questions per model and statement\n")
print(f"{'model':<28}{'statement':<11}{'correct':>8}{'Q8 ok':>7}{'varied':>8}{'in tok':>8}{'out tok':>8}"
      f"{'US$/call':>10}{'s/call':>8}")
for s in summary:
    print(f"{s['model']:<28}{s['statement']:<11}{s['correct']:>5}/{s['calls']}{s['correct_accepting_q8']:>4}/{s['calls']}"
          f"{len(s['questions_that_varied']):>8}{s['input_tokens_per_call']:>8,}{s['output_tokens_per_call']:>8,}"
          f"{s['cost_per_call']:>10.5f}{s['seconds_per_call']:>8.1f}")
wrong_by_q = {}
for s in summary:
    data = json.loads((HERE / "results" / f"accuracy-{s['model'].split('/')[1]}-{STATEMENTS[s['statement']].split('-')[1].split('.')[0]}{SUFFIX}.json").read_text())
    for r in data["runs"]:
        wrong_by_q.setdefault(r["q"], []).append(not r["ok_alt"])
print("\nWrong answers per question (all models and statements, Q8 accepted either way):")
print("  " + "  ".join(f"Q{q}: {sum(w)}/{len(w)}" for q, w in sorted(wrong_by_q.items())))
print(f"\nTotal cost of this run: US$ {sum(s['cost_total'] for s in summary):.4f}")
