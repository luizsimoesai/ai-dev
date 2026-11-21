"""
4. Reading the saved results: the ambiguous question and the length of the answers
==================================================================================

No API calls: reads results/accuracy-*.json from 1-accuracy.py.
Question 8 asks for "all individual expenses larger than 100 dollars". Is a
transfer to savings an expense? The question doesn't say. This script shows
which total each answer gave and whether the answer said which rule it used.

    uv run 4-read-results.py
"""

import json
from pathlib import Path

for path in sorted((Path(__file__).parent / "results").glob("accuracy-*.json")):
    data = json.loads(path.read_text())
    s, q8 = data["summary"], data["questions"][7]
    print(f"{s['model']}, {s['statement']} ({data['date']})")
    for r in (r for r in data["runs"] if r["q"] == 8):
        rule = "transfer" in r["text"].lower() or "savings" in r["text"].lower()
        kind = ("with the transfer" if r["answer"] == q8["expected"] else
                "without the transfer" if r["answer"] == q8["alternative"] else "neither")
        print(f"  Q8 run {r['run']}: {r['answer']} ({kind}); says which rule it used: {'yes' if rule else 'no'}")
    chars = sum(len(r["text"]) for r in data["runs"]) / len(data["runs"])
    print(f"  average answer length: {chars:.0f} characters\n")
