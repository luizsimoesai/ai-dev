"""
2. Long contracts on two API models
===================================

The same two questions (find one fact, count the clauses with a penalty) on
contracts of 40, 480 and 1,600 clauses (3 runs each) and 4,800 clauses (1 run,
because it is the expensive one). Reasoning stays at each model's default (on).
Reports input and reasoning tokens, the answer, the cost the API reports
(usage.cost) and the time. Saves results/long-context.json after every call;
if the run stops (for example, out of credits), running it again skips the
calls already saved and goes on from there.

Cost on 2026-11-21: US$ 1.24 for the whole run, most of it in the
1,600- and 4,800-clause calls (prices per token go up above a prompt size).

    uv run 2-long-context.py
"""

import json
import re
import time
from datetime import date

from contract import HERE, MODELS, QUESTIONS, build, client

PLAN = [(40, 3), (480, 3), (1600, 3), (4800, 1)]  # (clauses, runs)
MAX_TOKENS = 16000  # room for reasoning plus the answer
FORMAT = "End your reply with one line in the form 'FINAL ANSWER: <number>'."

RESULTS = HERE / "results" / "long-context.json"
api = client()
saved = json.loads(RESULTS.read_text()) if RESULTS.exists() else {"date": date.today().isoformat(), "calls": []}
calls = saved["calls"]
done = {(c["clauses"], c["model"], c["question"], c["run"]) for c in calls}
for n, runs in PLAN:
    contract, expected = build(n)
    for model in MODELS:
        for kind, question in QUESTIONS.items():
            for run in range(1, runs + 1):
                if (n, model, kind, run) in done:
                    continue
                start = time.time()
                resp = api.chat.completions.create(model=model, max_tokens=MAX_TOKENS, messages=[
                    {"role": "user", "content": f"{contract}\n\n{question} {FORMAT}"}])
                found = re.findall(r"FINAL ANSWER:\s*([\d,]+)", resp.choices[0].message.content or "")
                answer = int(found[-1].replace(",", "")) if found else None
                u = resp.usage
                calls.append({"id": resp.id, "clauses": n, "model": model, "question": kind, "run": run,
                              "input_tokens": u.prompt_tokens,
                              "reasoning_tokens": u.completion_tokens_details.reasoning_tokens,
                              "output_tokens": u.completion_tokens, "answer": answer, "expected": expected[kind],
                              "cost": u.model_extra["cost"], "seconds": round(time.time() - start, 1),
                              "finish_reason": resp.choices[0].finish_reason, "characters": len(contract),
                              "date": date.today().isoformat()})
                RESULTS.write_text(json.dumps(saved, indent=2))  # save after every call
                c = calls[-1]
                print(f"{n:>5} clauses  {model:<27} {kind:<6} run {run}  answer {answer}  expected {c['expected']}  "
                      f"US$ {c['cost']:.4f}  {c['seconds']}s", flush=True)

today = saved["date"]
print(f"\nSummary ({today}): right answers per setting, contract size, input tokens (where recorded), total cost\n")
print(f"{'clauses':>7}  {'characters':>10}  {'model':<27} {'question':<8} {'in tok':>8}  {'right':>5}  answers         US$ total")
for n, runs in PLAN:
    for model in MODELS:
        for kind in QUESTIONS:
            cs = [c for c in calls if c["clauses"] == n and c["model"] == model and c["question"] == kind]
            right = sum(c["answer"] == c["expected"] for c in cs)
            answers = ", ".join("none" if c["answer"] is None else str(c["answer"]) for c in cs)
            tokens = "-" if cs[0]["input_tokens"] is None else f"{cs[0]['input_tokens']:,}"
            print(f"{n:>7,}  {cs[0]['characters']:>10,}  {model:<27} {kind:<8} {tokens:>8}  {right}/{len(cs)}  "
                  f"{answers + ' (exp. ' + str(cs[0]['expected']) + ')':<15} {sum(c['cost'] for c in cs):.4f}")
print(f"\nTotal cost of this run: US$ {sum(c['cost'] for c in calls):.4f}")
