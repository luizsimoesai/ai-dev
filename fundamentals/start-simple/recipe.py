"""Shared pieces: the recipe, the scaling function, the check and the saved results.

The recipe is fictional: pancakes for 4, in metric units. The request is the
same in every script: adjust it for 6 people. One ingredient does not scale to
a whole number: 3 eggs for 4 people become 4.5 for 6. The app's rule, written
in scale(), is that eggs are counted whole and rounded up. The requests sent to
the models do not mention that rule, as in a real app where the rule lives in
the code.
"""

import json
import math
import os
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

HERE = Path(__file__).parent
MODELS = ["anthropic/claude-haiku-5.5", "openai/gpt-6-luna"]
REASONING = False  # set explicitly, never the provider default
SERVINGS = 6
REQUEST = f"Adjust the pancake recipe for {SERVINGS} people."

RECIPE = {
    "name": "pancakes",
    "servings": 4,
    "ingredients": [
        {"name": "flour", "quantity": 250, "unit": "g"},
        {"name": "milk", "quantity": 400, "unit": "ml"},
        {"name": "eggs", "quantity": 3, "unit": "whole"},
        {"name": "butter", "quantity": 40, "unit": "g"},
        {"name": "sugar", "quantity": 2, "unit": "tbsp"},
        {"name": "baking powder", "quantity": 2, "unit": "tsp"},
        {"name": "salt", "quantity": 0.5, "unit": "tsp"},
    ],
}
WHOLE_UNITS = {"whole"}  # the app's rule: these are counted whole, rounded up


def scale(recipe: dict, servings: int) -> dict:
    """The function: multiply every quantity, then apply the app's rule for whole items."""
    factor = servings / recipe["servings"]
    ingredients = []
    for item in recipe["ingredients"]:
        quantity = item["quantity"] * factor
        if item["unit"] in WHOLE_UNITS:
            quantity = math.ceil(quantity)  # 4.5 eggs -> 5 eggs
        ingredients.append({**item, "quantity": round(quantity, 2)})
    return {"name": recipe["name"], "servings": servings, "ingredients": ingredients}


EXPECTED = scale(RECIPE, SERVINGS)["ingredients"]


def check(ingredients: list[dict]) -> list[str]:
    """The criterion, in code: every ingredient as scale() returns it. Returns the differences."""
    got = {i["name"].strip().lower(): i for i in ingredients}
    problems = []
    for want in EXPECTED:
        item = got.get(want["name"])
        if item is None:
            problems.append(f"{want['name']}: missing")
        elif item["unit"].strip().lower() != want["unit"] or abs(item["quantity"] - want["quantity"]) > 0.01:
            problems.append(f"{want['name']}: {item['quantity']:g} {item['unit']} "
                            f"(the app's answer is {want['quantity']:g} {want['unit']})")
    return problems


def quantity_of(ingredients: list[dict], name: str) -> str:
    item = next((i for i in ingredients if i["name"].strip().lower() == name), None)
    return "missing" if item is None else f"{item['quantity']:g} {item['unit']}"


def get_recipe() -> dict:
    """Read-only tool: the recipe as stored."""
    return RECIPE


def scale_recipe(servings: int) -> dict:
    """Tool: the scale() function above, exposed to the agent."""
    return scale(RECIPE, servings)


INGREDIENTS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {"name": {"type": "string"}, "quantity": {"type": "number"}, "unit": {"type": "string"}},
        "required": ["name", "quantity", "unit"],
        "additionalProperties": False,
    },
}


def client() -> OpenAI:
    load_dotenv(HERE / ".env")
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])


def call_model(api: OpenAI, model: str, messages: list, schema_name: str, schema: dict):
    """One call with reasoning off and a strict JSON Schema; returns the response and the seconds it took."""
    start = time.perf_counter()
    resp = api.chat.completions.create(
        model=model, max_tokens=500, messages=messages,
        response_format={"type": "json_schema", "json_schema": {"name": schema_name, "strict": True, "schema": schema}},
        extra_body={"reasoning": {"enabled": REASONING}, "provider": {"require_parameters": True}})
    return resp, time.perf_counter() - start


class Results:
    """Saves every call to results/<name>.json and replays saved calls, so a stopped run resumes."""

    def __init__(self, name: str):
        self.path = HERE / "results" / f"{name}.json"
        self.path.parent.mkdir(exist_ok=True)
        self.data = (json.loads(self.path.read_text()) if self.path.exists()
                     else {"date": date.today().isoformat(), "reasoning": REASONING, "calls": []})

    def get(self, model: str, step: int) -> dict | None:
        return next((c for c in self.data["calls"] if (c["model"], c["step"]) == (model, step)), None)

    def add(self, model: str, step: int, resp, seconds: float) -> dict:
        call = {"id": resp.id, "model": model, "provider": resp.model_extra.get("provider"), "step": step,
                "reply": (resp.choices[0].message.content or "").strip(),
                "input_tokens": resp.usage.prompt_tokens, "output_tokens": resp.usage.completion_tokens,
                "cost": resp.usage.model_extra["cost"], "seconds": round(seconds, 2),
                "date": date.today().isoformat()}
        self.data["calls"].append(call)
        self.path.write_text(json.dumps(self.data, indent=2))  # save after every call
        return call

    def summary(self, model: str) -> str:
        calls = [c for c in self.data["calls"] if c["model"] == model]
        return (f"{len(calls)} LLM call{'' if len(calls) == 1 else 's'}, US$ {sum(c['cost'] for c in calls):.5f}, "
                f"{sum(c['seconds'] for c in calls):.1f} s")
