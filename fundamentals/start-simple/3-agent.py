"""
3. Scaling a recipe with an agent
=================================

The same request, as an agent: the loop of fundamentals/what-an-agent-is with
two tools, get_recipe and scale_recipe (the scale() function itself). At each
step the model picks one JSON action with a strict schema, the code checks it
and runs the tool, and the result goes back as an observation. The loop stops
at an answer or after MAX_STEPS. The code checks the final ingredients against
scale().

    uv run --with-requirements requirements.txt 3-agent.py   # needs OPENROUTER_API_KEY in .env

Saves results/agent.json after every call; if the run stops, running it again
replays the saved steps and continues from there.
"""

import json

from recipe import (INGREDIENTS_SCHEMA, MODELS, REASONING, REQUEST, Results, call_model, check, client, get_recipe,
                    quantity_of, scale_recipe)

MAX_STEPS = 6
SYSTEM = """You help users adjust recipes. You work in steps. At each step, reply with one JSON action:
- get_recipe: see the recipe, with its servings and ingredients. Set servings to 0 and ingredients to [].
- scale_recipe: scale the recipe to a number of servings. Set servings to that number and ingredients to [].
- answer: your final answer. Set servings and the adjusted ingredients (name, quantity, unit).
After each action you get an Observation."""

ACTION_SCHEMA = {  # strict mode: every field is required, so the unused ones are 0 or []
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["get_recipe", "scale_recipe", "answer"]},
        "servings": {"type": "integer"},
        "ingredients": INGREDIENTS_SCHEMA,
    },
    "required": ["action", "servings", "ingredients"],
    "additionalProperties": False,
}

api = client()
results = Results("agent")


def check_action(reply: str) -> tuple[dict | None, str | None]:
    """The code checks the model's reply before anything runs. Returns (action, None) or (None, error)."""
    try:
        action = json.loads(reply)
    except json.JSONDecodeError:
        return None, "the reply must be exactly one JSON action"
    if not isinstance(action, dict) or set(action) != set(ACTION_SCHEMA["required"]):
        return None, "the reply does not follow the action schema"
    if action["action"] not in ACTION_SCHEMA["properties"]["action"]["enum"]:
        return None, f"unknown action {action['action']!r}"
    if action["action"] == "scale_recipe" and not 1 <= action["servings"] <= 100:
        return None, "servings must be between 1 and 100"
    return action, None


def decide(model: str, step: int, messages: list) -> str:
    call = results.get(model, step)
    if call is None:  # not saved yet: call the model
        call = results.add(model, step, *call_model(api, model, messages, "action", ACTION_SCHEMA))
    return call["reply"]


def run(model: str) -> tuple[list[str], list[dict] | None]:
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": REQUEST}]
    steps = []
    for step in range(1, MAX_STEPS + 1):
        reply = decide(model, step, messages)                             # DECIDE: the model picks the next step
        action, error = check_action(reply)                               # the code checks it before anything runs
        if action and action["action"] == "answer":
            return steps + ["answer"], action["ingredients"]
        if error:
            steps.append("blocked")
            result = {"error": error}
        elif action["action"] == "get_recipe":
            steps.append("get_recipe")
            result = get_recipe()                                         # ACT: read-only
        else:
            steps.append(f"scale_recipe({action['servings']})")
            result = scale_recipe(action["servings"])                     # ACT: the function
        messages += [{"role": "assistant", "content": reply},
                     {"role": "user", "content": f"Observation: {json.dumps(result)}"}]  # OBSERVE
    return steps + ["stop"], None


print(f"Reasoning {'on' if REASONING else 'off'} ({results.data['date']}), at most {MAX_STEPS} steps")
for model in MODELS:
    steps, ingredients = run(model)
    problems = check(ingredients) if ingredients is not None else ["no answer"]
    print(f"\n{model}")
    print(f"  steps: {' > '.join(steps)}")
    print(f"  right: {'yes' if not problems else 'no'}")
    if ingredients is not None:
        print(f"  eggs:  {quantity_of(ingredients, 'eggs')}")
    for problem in problems:
        print(f"  differs: {problem}")
    print(f"  total: {results.summary(model)}")
