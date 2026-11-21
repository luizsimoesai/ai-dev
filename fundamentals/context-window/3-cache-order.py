"""
3. Add at the end: where new text goes decides the cache
========================================================

The contract (170 clauses) sits in the system message. Three calls per model:
a first question; then an amendment added after the contract; then the same
amendment placed before the contract. The output shows how many input tokens
came from the provider's cache and what each call cost.

Anthropic models only cache when the request marks the block to keep
("cache_control"); OpenAI models cache repeated prefixes automatically.
Each model is pinned to its own vendor's endpoint so the cache can be reused.
A random reference line at the top makes every run start with an empty cache.

    uv run 3-cache-order.py
"""

import time
import uuid
from datetime import date

from contract import MODELS, QUESTIONS, build, client

api = client()
contract, _ = build(170)
contract = f"Contract reference {uuid.uuid4()}\n\n{contract}"  # new text on every run: the first call starts with an empty cache
amendment = "Amendment 1. The notice period for termination for convenience is changed to 60 days."
question = QUESTIONS["needle"] + " Reply with the number only."

print(f"Cache and order ({date.today().isoformat()})\n")
for model in MODELS:
    doc = {"type": "text", "text": contract}
    if model.startswith("anthropic/"):
        doc["cache_control"] = {"type": "ephemeral"}  # ask Anthropic to cache everything up to here
    vendor = "Anthropic" if model.startswith("anthropic/") else "OpenAI"
    cases = [
        ("first question", [{"role": "system", "content": [doc]}, {"role": "user", "content": question}]),
        ("amendment after the contract", [{"role": "system", "content": [doc]},
                                          {"role": "user", "content": f"{amendment}\n\n{question}"}]),
        ("amendment before the contract", [{"role": "system", "content": [{"type": "text", "text": amendment}, doc]},
                                           {"role": "user", "content": question}]),
    ]
    for label, messages in cases:
        resp = api.chat.completions.create(model=model, max_tokens=2000, messages=messages,
                                           extra_body={"provider": {"order": [vendor], "allow_fallbacks": False}})
        u = resp.usage
        print(f"{model:<27} {label:<30} {u.prompt_tokens:,} in, {u.prompt_tokens_details.cached_tokens or 0:>6,} cached  "
              f"answer {(resp.choices[0].message.content or '').strip():>3}  US$ {u.model_extra['cost']:.5f}")
        time.sleep(3)
    print()
