"""
1. Scaling a recipe with a function
===================================

No LLM: the recipe is already structured and the number of servings comes from
the app, so plain code multiplies every quantity and applies the app's rule
for whole items (eggs are rounded up).

    uv run --with-requirements requirements.txt 1-function.py   # no API key needed
"""

import time

from recipe import RECIPE, SERVINGS, scale

start = time.perf_counter()
scaled = scale(RECIPE, SERVINGS)
seconds = time.perf_counter() - start

print(f"Pancakes, {RECIPE['servings']} -> {SERVINGS} servings (code, no LLM)")
for before, after in zip(RECIPE["ingredients"], scaled["ingredients"]):
    exact = before["quantity"] * SERVINGS / RECIPE["servings"]
    note = f"   ({exact:g}, rounded up by the app's rule)" if after["quantity"] != exact else ""
    print(f"  {after['name']:<14}{after['quantity']:>6g} {after['unit']}{note}")
print(f"  total: 0 LLM calls, US$ 0, {seconds:.6f} s")
