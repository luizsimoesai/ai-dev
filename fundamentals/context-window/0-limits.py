"""
0. Context limits, right now
============================

The context window of each API model (input plus answer, in tokens) and the
longest answer it allows, read from OpenRouter's public model list. No API
key needed.

    uv run 0-limits.py
"""

import json
import urllib.request
from datetime import date

from contract import MODELS

with urllib.request.urlopen("https://openrouter.ai/api/v1/models") as resp:
    listed = {m["id"]: m for m in json.load(resp)["data"]}

print(f"Context limits on {date.today().isoformat()}, in tokens\n")
for model in MODELS:
    m = listed[model]
    print(f"{model:<27} context {m['context_length']:>9,}  longest answer {m['top_provider']['max_completion_tokens']:>7,}")
