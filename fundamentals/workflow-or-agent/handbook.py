"""Shared pieces: the handbook, the questions, the checks and the saved results.

The handbook is fictional: four short policy documents, amounts in US dollars.
Two details make the questions interesting:
- remote-work says coworking is reimbursed "under the expenses policy", and
  the monthly cap is only in expenses, so that answer is split across two
  documents;
- parental leave is not in the handbook at all.
"""

import json
import os
import re
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

HERE = Path(__file__).parent
MODELS = ["anthropic/claude-haiku-5.5", "openai/gpt-6-luna"]
REASONING = False  # set explicitly, never the provider default
NOT_COVERED = "The handbook does not cover this."

DOCS = {  # name -> title, topics (used only by the workflow) and text
    "travel": {
        "title": "Business travel",
        "topics": {"travel", "trip", "flight", "flights", "hotel", "train", "book", "booking"},
        "text": "# Business travel\n"
                "- Book flights at least 14 days before departure, through the travel portal.\n"
                "- Fly economy on flights under 6 hours; premium economy is allowed on longer flights.\n"
                "- Hotels: up to 180 dollars per night.\n"
                "- If the trip takes under 4 hours by train, take the train instead of flying.",
    },
    "expenses": {
        "title": "Expenses and reimbursement",
        "topics": {"expense", "expenses", "reimburse", "reimbursed", "reimbursement", "receipt", "receipts", "meal", "meals"},
        "text": "# Expenses and reimbursement\n"
                "- Submit expenses within 30 days, with a receipt for anything over 25 dollars.\n"
                "- Meals while traveling: up to 60 dollars per day.\n"
                "- Coworking spaces: up to 300 dollars per month, with your manager's approval before you sign up.\n"
                "- Not reimbursed: fines, personal entertainment and upgrades you chose.",
    },
    "remote-work": {
        "title": "Working remotely",
        "topics": {"remote", "home", "abroad", "country", "work", "coworking"},
        "text": "# Working remotely\n"
                "- You can work from home up to 3 days per week.\n"
                "- Working from another country: up to 30 days per year. Tell HR at least 10 days before you go.\n"
                "- Coworking spaces are reimbursed under the expenses policy.",
    },
    "equipment": {
        "title": "Equipment",
        "topics": {"equipment", "laptop", "laptops", "monitor", "chair", "computer", "office"},
        "text": "# Equipment\n"
                "- Laptops are replaced every 3 years, or sooner if they break.\n"
                "- Home office: one monitor and one chair, up to 250 dollars in total.\n"
                "- Return all equipment on your last day.",
    },
}

QUESTIONS = {
    "flight-booking": "How many days before a business trip do I need to book my flight?",
    "coworking-abroad": "I'll work from Lisbon for two weeks next month. "
                        "Can I get my coworking space reimbursed, and up to how much?",
    "parental-leave": "How many weeks of parental leave do I get?",
}


def is_right(question: str, answer: str) -> bool:
    """The criteria, in code: the facts a right answer must contain."""
    a = answer.lower()
    if question == "flight-booking":
        return "14" in a
    if question == "coworking-abroad":
        return "300" in a and "approv" in a  # the cap and the manager's approval, both in expenses
    return NOT_COVERED.lower().rstrip(".") in a


def list_documents() -> list[dict]:
    """Read-only tool: the names and titles of the documents."""
    return [{"name": name, "title": doc["title"]} for name, doc in DOCS.items()]


def read_document(name: str) -> dict:
    """Read-only tool: the full text of one document."""
    return {"name": name, "text": DOCS[name]["text"]}


def client() -> OpenAI:
    load_dotenv(HERE / ".env")
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])


def call_model(api: OpenAI, model: str, messages: list, **kwargs):
    """One call with reasoning off; returns the response and the seconds it took."""
    start = time.perf_counter()
    resp = api.chat.completions.create(model=model, max_tokens=300, messages=messages,
                                       extra_body={"reasoning": {"enabled": REASONING}, **kwargs.pop("extra_body", {})},
                                       **kwargs)
    return resp, time.perf_counter() - start


class Results:
    """Saves every call to results/<name>.json and replays saved calls, so a stopped run resumes."""

    def __init__(self, name: str):
        self.path = HERE / "results" / f"{name}.json"
        self.path.parent.mkdir(exist_ok=True)
        self.data = (json.loads(self.path.read_text()) if self.path.exists()
                     else {"date": date.today().isoformat(), "reasoning": REASONING, "calls": []})

    def get(self, model: str, question: str, step: int) -> dict | None:
        return next((c for c in self.data["calls"]
                     if (c["model"], c["question"], c["step"]) == (model, question, step)), None)

    def add(self, model: str, question: str, step: int, resp, seconds: float) -> dict:
        call = {"id": resp.id, "model": model, "provider": resp.model_extra.get("provider"),
                "question": question, "step": step, "reply": (resp.choices[0].message.content or "").strip(),
                "input_tokens": resp.usage.prompt_tokens, "output_tokens": resp.usage.completion_tokens,
                "cost": resp.usage.model_extra["cost"], "seconds": round(seconds, 2),
                "date": date.today().isoformat()}
        self.data["calls"].append(call)
        self.path.write_text(json.dumps(self.data, indent=2))  # save after every call
        return call

    def summary(self, model: str) -> str:
        calls = [c for c in self.data["calls"] if c["model"] == model]
        return (f"{len(calls)} LLM calls, US$ {sum(c['cost'] for c in calls):.5f}, "
                f"{sum(c['seconds'] for c in calls):.1f} s")


def words(text: str) -> set[str]:
    return set(re.findall(r"[a-z]+", text.lower()))
