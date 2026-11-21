"""
0. Prices and providers, right now
==================================

Every model on OpenRouter can be served by several providers. Each one has its
own price per million tokens and its own list of supported features. Some
charge more per token once the prompt passes a size; those tiers are printed
under each provider. This script reads the public endpoint list (no API key
needed) and prints all of it.

    uv run 0-prices.py
"""

import json
import urllib.request
from datetime import date

from common import MODELS


def usd(x: float) -> str:
    """Two decimals, or three when the third one matters (0.375)."""
    return f"{x:.3f}" if round(x, 2) != round(x, 3) else f"{x:.2f}"

print(f"Prices on {date.today().isoformat()}, in US$ per million tokens\n")
for model in MODELS:
    url = f"https://openrouter.ai/api/v1/models/{model}/endpoints"
    with urllib.request.urlopen(url) as resp:
        endpoints = json.load(resp)["data"]["endpoints"]
    print(model)
    for e in endpoints:
        p = {k: float(e["pricing"].get(k) or 0) * 1e6 for k in ("prompt", "completion", "input_cache_read")}
        print(f"  {e['provider_name']:<24} input {usd(p['prompt'])}  output {usd(p['completion'])}  "
              f"cached input {p['input_cache_read']:.3f}  "
              f"structured outputs: {'yes' if 'structured_outputs' in e.get('supported_parameters', []) else 'no'}")
        for o in e["pricing"].get("overrides", []):  # long-context tiers
            q = {k: float(o.get(k) or 0) * 1e6 for k in ("prompt", "completion", "input_cache_read")}
            print(f"  {'':<24} above {o['min_prompt_tokens']:,} input tokens: input {usd(q['prompt'])}  "
                  f"output {usd(q['completion'])}  cached input {q['input_cache_read']:.3f}")
    print()
