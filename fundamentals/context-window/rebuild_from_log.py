"""
Rebuild results/long-context.json from a run log
================================================

The 2026-11-21 run of 2-long-context.py stopped at call 39 of 40 (the API key
ran out of credit) while the script still saved its results only at the end.
This script reads what it printed (results/long-context-run.log) and writes
those calls to results/long-context.json, so 2-long-context.py can resume.
The log has the answer, the cost and the time of each call, but not the token
counts, so those fields stay empty (null) for the rebuilt calls.

    uv run rebuild_from_log.py
"""

import json
import re

from contract import HERE, build

LINE = re.compile(r"^\s*([\d,]+) clauses\s+(\S+)\s+(needle|count)\s+run (\d)\s+answer (\S+)\s+expected (\d+)\s+"
                  r"US\$ ([\d.]+)\s+([\d.]+)s$")

log = (HERE / "results" / "long-context-run.log").read_text().splitlines()
calls, size = [], {}
for line in log:
    m = LINE.match(line)
    if not m:
        continue
    n = int(m[1].replace(",", ""))
    if n not in size:
        size[n] = len(build(n)[0])
    calls.append({"clauses": n, "model": m[2], "question": m[3], "run": int(m[4]),
                  "input_tokens": None, "reasoning_tokens": None, "output_tokens": None,
                  "answer": None if m[5] == "None" else int(m[5]), "expected": int(m[6]),
                  "cost": float(m[7]), "seconds": float(m[8]), "finish_reason": None,
                  "characters": size[n], "date": "2026-11-21", "source": "run log"})

(HERE / "results" / "long-context.json").write_text(json.dumps({"date": "2026-11-21", "calls": calls}, indent=2))
print(f"{len(calls)} calls rebuilt from the log, US$ {sum(c['cost'] for c in calls):.4f}")
