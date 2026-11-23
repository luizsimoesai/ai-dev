"""Shared pieces: the trip request, the fictional flights and the search tool.

The flights are the agent's environment: made-up flight numbers and prices in
US dollars, Lisbon (LIS) to Rome (FCO) only. No flight on 2026-12-12 fits the
150-dollar budget; one on 2026-12-13 does, and none on 2026-12-11. So an agent
that searches the requested date has to look at the result and decide again.
"""

import json
import os
import re
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

HERE = Path(__file__).parent
MODELS = ["anthropic/claude-haiku-5.5", "openai/gpt-6-luna"]
REASONING = False  # set explicitly, never the provider default

REQUEST = ("Find me a one-way flight from Lisbon to Rome on 2026-12-12 for at most 150 dollars. "
           "I can fly one day earlier or later if needed.")
ALLOWED_DATES = {"2026-12-11", "2026-12-12", "2026-12-13"}  # the window the user allowed

FLIGHTS = {  # (origin, destination, date) -> [(flight, departure, price in US dollars)]
    ("LIS", "FCO", "2026-12-11"): [("FX 211", "07:05", 162), ("FX 219", "18:40", 171)],
    ("LIS", "FCO", "2026-12-12"): [("FX 301", "09:15", 184), ("FX 305", "14:30", 179), ("FX 309", "20:05", 245)],
    ("LIS", "FCO", "2026-12-13"): [("FX 401", "06:50", 128), ("FX 407", "12:10", 196)],
}
CITY_AIRPORTS = {"ROM": ["FCO", "CIA"]}  # an IATA city code covers all of the city's airports, as in real searches


def search_flights(origin: str, destination: str, date: str) -> list[dict]:
    """The only tool: read-only, it searches and never books. Accepts airport or city codes."""
    return [{"flight": f, "from": o, "to": d, "departs": t, "price_usd": p}
            for o in CITY_AIRPORTS.get(origin, [origin])
            for d in CITY_AIRPORTS.get(destination, [destination])
            for f, t, p in FLIGHTS.get((o, d, date), [])]


def check(reply: str) -> tuple[dict | None, str | None]:
    """The code checks the model's reply before anything runs. Returns (action, None) or (None, error).

    A strict schema is requested, but the reply is still only text: it can be
    several JSON objects, or a search with a date the user did not allow.
    """
    try:
        action = json.loads(reply)
    except json.JSONDecodeError:
        return None, "the reply must be exactly one JSON action"
    if not isinstance(action, dict) or set(action) != set(ACTION_SCHEMA["required"]):
        return None, "the reply does not follow the action schema"
    if action["action"] == "answer":
        return action, None
    if action["action"] != "search_flights":
        return None, f"unknown action {action['action']!r}"
    if not all(re.fullmatch(r"[A-Z]{3}", action[k]) for k in ("origin", "destination")):
        return None, "origin and destination must be 3-letter IATA codes"
    if action["date"] not in ALLOWED_DATES:
        return None, f"date {action['date']!r} is outside the dates the user allowed"
    return action, None


ACTION_SCHEMA = {  # strict mode: every field is required, so the unused ones are empty strings
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["search_flights", "answer"]},
        "origin": {"type": "string"},
        "destination": {"type": "string"},
        "date": {"type": "string"},
        "text": {"type": "string"},
    },
    "required": ["action", "origin", "destination", "date", "text"],
    "additionalProperties": False,
}


def client() -> OpenAI:
    load_dotenv(HERE / ".env")
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])


class Results:
    """Saves every call to results/<name>.json and replays saved calls, so a stopped run resumes."""

    def __init__(self, name: str):
        self.path = HERE / "results" / f"{name}.json"
        self.path.parent.mkdir(exist_ok=True)
        self.data = (json.loads(self.path.read_text()) if self.path.exists()
                     else {"date": date.today().isoformat(), "reasoning": REASONING, "calls": []})

    def get(self, model: str, step: int) -> dict | None:
        return next((c for c in self.data["calls"] if c["model"] == model and c["step"] == step), None)

    def add(self, model: str, step: int, resp) -> dict:
        call = {"id": resp.id, "model": model, "provider": resp.model_extra.get("provider"), "step": step,
                "reply": (resp.choices[0].message.content or "").strip(),
                "input_tokens": resp.usage.prompt_tokens, "output_tokens": resp.usage.completion_tokens,
                "cost": resp.usage.model_extra["cost"], "date": date.today().isoformat()}
        self.data["calls"].append(call)
        self.path.write_text(json.dumps(self.data, indent=2))  # save after every call
        return call

    def cost(self) -> float:
        return sum(c["cost"] for c in self.data["calls"])
