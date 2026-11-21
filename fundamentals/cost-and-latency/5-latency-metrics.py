"""
5. TTFT and TPOT, from the saved latency results
================================================

No API calls: reads results/latency.json (written by 2-latency.py) and names
the two parts of the wait.

  - TTFT (time to first token): from the request to the first token of the
    visible answer. With reasoning on, it includes the hidden reasoning tokens.
  - TPOT (time per output token): the time per answer token after the first,
    (total - TTFT) / (answer tokens - 1).

Total latency is about TTFT + TPOT x output tokens. The script prints the
medians of the runs for each setting, and that estimate next to the median
measured total.

    uv run 5-latency-metrics.py
"""

import json
from statistics import median

from common import HERE

data = json.loads((HERE / "results" / "latency.json").read_text())
print(f"TTFT and TPOT, medians of {len(data['results'][0]['runs'])} runs ({data['date']})\n")
print(f"{'model':<27} {'stmt':<5} {'setting':<23} {'reason':>6} {'answer':>6} {'TTFT s':>6} "
      f"{'TPOT ms':>7} {'TTFT+TPOTxN':>11} {'total s':>7}")
for r in data["results"]:
    runs = r["runs"]
    ttft = median(x["first_answer_s"] for x in runs)
    tpot = median((x["total_s"] - x["first_answer_s"]) / (x["answer_tokens"] - 1) for x in runs)
    answer = median(x["answer_tokens"] for x in runs)
    estimate = ttft + tpot * answer
    stmt = "3m" if r["statement"].startswith("3") else "12m"
    print(f"{r['model']:<27} {stmt:<5} {r['setting']:<23} {median(x['reasoning_tokens'] for x in runs):>6,.0f} "
          f"{answer:>6,.0f} {ttft:>6.1f} {tpot * 1000:>7.1f} {estimate:>11.1f} {median(x['total_s'] for x in runs):>7.1f}")
