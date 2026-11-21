"""Shared pieces: the models, the statements, the questions and the API client.

The expected answers are computed in plain Python from the same CSV, so the
grading is exact (tolerance: 1 cent).
"""

import csv
import os
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
MODELS = ["anthropic/claude-haiku-5.5", "openai/gpt-6-luna"]  # two vendors, via OpenRouter
STATEMENTS = {"3 months": "statement-3m.csv", "12 months": "statement-12m.csv"}

SYSTEM = "You are a helpful assistant that answers questions about the user's bank statement."
FORMAT = ("Report money spent as a positive number. "
          "End your reply with one line in the form 'FINAL ANSWER: <number>' (no currency symbol, no thousands separator).")


def client():
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv(HERE / ".env")
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])


def load(name: str) -> tuple[str, list[dict]]:
    text = (HERE / name).read_text()
    rows = [{**r, "amount": float(r["amount"])} for r in csv.DictReader(text.splitlines())]
    return text, rows


def messages(csv_text: str, question: str) -> list[dict]:
    """The whole statement goes in every request: that's the v0 approach."""
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"My bank statement (CSV):\n\n{csv_text}\n\n{question}\n\n{FORMAT}"},
    ]


def questions(rows: list[dict]) -> list[dict]:
    """Ten questions and their expected answers, computed from the rows."""
    month = lambda r: r["date"][:7]
    spent = lambda rs: round(-sum(r["amount"] for r in rs if r["amount"] < 0), 2)
    groc_aug = [r for r in rows if r["category"] == "groceries" and month(r) == "2026-08"]
    oct_out = [r for r in rows if month(r) == "2026-10" and r["amount"] < 0]
    rest = defaultdict(float)
    for r in rows:
        if r["category"] == "restaurants":
            rest[month(r)] += -r["amount"]
    q = lambda text, value, alt=None: {"question": text, "expected": round(value, 2),
                                       "alternative": None if alt is None else round(alt, 2)}
    return [
        q("How much did I spend on groceries in October 2026?",
          spent(r for r in rows if r["category"] == "groceries" and month(r) == "2026-10")),
        q("How many restaurant transactions did I have in September 2026?",
          sum(1 for r in rows if r["category"] == "restaurants" and month(r) == "2026-09")),
        q("What was my total income (category income) in August 2026?",
          sum(r["amount"] for r in rows if r["category"] == "income" and month(r) == "2026-08")),
        q("What was the net change of my account in September 2026 (sum of all amounts, keep the sign)?",
          sum(r["amount"] for r in rows if month(r) == "2026-09")),
        q("How much did I spend at METRO TRANSIT in total, across all months?",
          spent(r for r in rows if r["description"] == "METRO TRANSIT")),
        q("What was the average grocery purchase amount in August 2026?",
          spent(groc_aug) / len(groc_aug)),
        q("How much did I spend on subscriptions over the whole period?",
          spent(r for r in rows if r["category"] == "subscriptions")),
        # Ambiguous on purpose: is a transfer to savings an expense? The
        # alternative answer leaves it out.
        q("What is the sum of all individual expenses larger than 100 dollars in October 2026?",
          spent(r for r in oct_out if -r["amount"] > 100),
          spent(r for r in oct_out if -r["amount"] > 100 and r["category"] != "transfers")),
        q("How much did I spend on transport in September 2026?",
          spent(r for r in rows if r["category"] == "transport" and month(r) == "2026-09")),
        q("By how much did my restaurant spending in October 2026 exceed September 2026?",
          rest["2026-10"] - rest["2026-09"]),
    ]
