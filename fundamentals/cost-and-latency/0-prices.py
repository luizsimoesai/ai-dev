"""
0. Prices and providers, right now
==================================

Every model on OpenRouter can be served by several providers. Each one has its
own price per million tokens and its own list of supported features. This
script reads the public endpoint list (no API key needed) and prints both.

    uv run 0-prices.py
"""

import json
import urllib.request
from datetime import date

from common import MODELS

print(f"Prices on {date.today().isoformat()}, in US$ per million tokens\n")
for model in MODELS:
    url = f"https://openrouter.ai/api/v1/models/{model}/endpoints"
    with urllib.request.urlopen(url) as resp:
        endpoints = json.load(resp)["data"]["endpoints"]
    print(model)
    for e in endpoints:
        p = {k: float(e["pricing"].get(k) or 0) * 1e6 for k in ("prompt", "completion", "input_cache_read")}
        print(f"  {e['provider_name']:<24} input {p['prompt']:.2f}  output {p['completion']:.2f}  "
              f"cached input {p['input_cache_read']:.3f}  "
              f"structured outputs: {'yes' if 'structured_outputs' in e.get('supported_parameters', []) else 'no'}")
    print()
