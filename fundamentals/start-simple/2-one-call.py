"""
2. Scaling a recipe with one LLM call
=====================================

The same request, with the model doing the arithmetic: one call per model gets
the recipe as JSON and the user's request, and returns the scaled ingredients
with a strict JSON Schema. The request does not mention the app's rule for
eggs. The code checks the reply against scale().

    uv run --with-requirements requirements.txt 2-one-call.py   # needs OPENROUTER_API_KEY in .env

Saves results/one-call.json after every call; running it again replays the
saved calls.
"""

import json

from recipe import INGREDIENTS_SCHEMA, MODELS, REASONING, RECIPE, REQUEST, SERVINGS, Results, call_model, check, client, quantity_of

SYSTEM = "You adjust recipes. Keep each ingredient's name and unit exactly as given. Reply with the adjusted ingredients."
SCHEMA = {"type": "object", "properties": {"ingredients": INGREDIENTS_SCHEMA},
          "required": ["ingredients"], "additionalProperties": False}

api = client()
results = Results("one-call")

print(f"Reasoning {'on' if REASONING else 'off'} ({results.data['date']}), {RECIPE['servings']} -> {SERVINGS} servings")
for model in MODELS:
    call = results.get(model, 1)
    if call is None:  # not saved yet: call the model
        messages = [{"role": "system", "content": SYSTEM},
                    {"role": "user", "content": f"Recipe: {json.dumps(RECIPE)}\n\n{REQUEST}"}]
        call = results.add(model, 1, *call_model(api, model, messages, "recipe", SCHEMA))
    ingredients = json.loads(call["reply"])["ingredients"]               # the model did the arithmetic
    problems = check(ingredients)                                       # the code checks every ingredient
    print(f"\n{model}")
    print(f"  right: {'yes' if not problems else 'no'}")
    print(f"  eggs:  {quantity_of(ingredients, 'eggs')}")
    for problem in problems:
        print(f"  differs: {problem}")
    print(f"  total: {results.summary(model)}")
