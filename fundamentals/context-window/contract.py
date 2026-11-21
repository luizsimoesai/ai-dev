"""Shared pieces: a synthetic supply contract, two questions and the API client.

The contract has N numbered clauses built from a fixed seed, so every run sees
the same text. Two questions, with answers computed in Python:

- needle: one fact that appears in a single clause (the notice period);
- count:  how many clauses carry a late-performance penalty (spread all over).

Every name, clause and amount is made up.
"""

import os
import random
from pathlib import Path

HERE = Path(__file__).parent
MODELS = ["anthropic/claude-haiku-5.5", "openai/gpt-6-luna"]  # two vendors, via OpenRouter

TOPICS = ["Delivery", "Payment", "Warranty", "Confidentiality", "Insurance", "Audit", "Subcontracting",
          "Notices", "Data protection", "Force majeure", "Acceptance testing", "Intellectual property"]
FILLER = [
    "The Supplier shall keep complete and accurate records of all work performed under this Agreement.",
    "Any change to the scope must be agreed in writing by authorized representatives of both parties.",
    "The Customer may request reasonable information about the progress of the services at any time.",
    "Each party shall bear its own costs in connection with the negotiation of this Agreement.",
    "Obligations under this clause survive the termination or expiry of this Agreement.",
    "The parties shall cooperate in good faith to resolve any issue arising under this clause.",
    "Nothing in this clause limits any right or remedy available to either party under applicable law.",
]
NOTICE_DAYS = 47

QUESTIONS = {
    "needle": "How many days' written notice are required to terminate this Agreement for convenience?",
    "count": "How many clauses contain a late-performance penalty?",
}


def build(n_clauses: int, seed: int = 7) -> tuple[str, dict]:
    """Return the contract text and the expected answer to each question."""
    r = random.Random(seed)
    clauses, penalties = [], 0
    needle_at = n_clauses * 2 // 3  # the fact sits two thirds of the way in
    for i in range(1, n_clauses + 1):
        topic = r.choice(TOPICS)
        body = " ".join(r.sample(FILLER, 3))
        if r.random() < 0.25:
            fee = r.choice([250, 400, 500, 750, 1000, 1200, 1500])
            body += f" A late-performance penalty of {fee} dollars applies to each breach of this clause."
            penalties += 1
        if i == needle_at:
            topic = "Termination"
            body = (f"Either party may terminate this Agreement for convenience by giving {NOTICE_DAYS} days' "
                    "written notice to the other party. " + body)
        clauses.append(f"Clause {i}. {topic}. {body}")
    return "\n\n".join(clauses), {"needle": NOTICE_DAYS, "count": penalties}


def client():
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv(HERE / ".env")
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
