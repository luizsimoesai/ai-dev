"""Shared pieces: the models, one LLM call, the saved results and the project files.

The codebase is fictional: shortlinks (project/), a small link shortener with
three modules and six tests. One test fails on purpose: is_expired() uses >
where the test expects a link to expire on day 90.
"""

import json
import os
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

HERE = Path(__file__).parent
PROJECT = HERE / "project"
MODELS = ["anthropic/claude-haiku-5.5", "openai/gpt-6-luna"]
REASONING = False  # set explicitly, never the provider default


def project_files() -> dict[str, str]:
    """Every Python file in the project: path -> text."""
    return {str(p.relative_to(PROJECT)): p.read_text() for p in sorted(PROJECT.rglob("*.py"))}


def client() -> OpenAI:
    load_dotenv(HERE / ".env")
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])


def call_model(api: OpenAI, model: str, messages: list, schema_name: str, schema: dict):
    """One call with reasoning off and a strict JSON Schema; returns the response and the seconds it took."""
    start = time.perf_counter()
    resp = api.chat.completions.create(
        model=model, max_tokens=800, messages=messages,
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
        self.api = None

    def ask(self, model: str, step: str, messages: list, schema_name: str, schema: dict) -> dict:
        """The saved call for (model, step), or a new call to the model, saved right away."""
        saved = next((c for c in self.data["calls"] if (c["model"], c["step"]) == (model, step)), None)
        if saved:
            return saved
        self.api = self.api or client()
        resp, seconds = call_model(self.api, model, messages, schema_name, schema)
        call = {"id": resp.id, "model": model, "provider": resp.model_extra.get("provider"), "step": step,
                "reply": (resp.choices[0].message.content or "").strip(),
                "input_tokens": resp.usage.prompt_tokens, "output_tokens": resp.usage.completion_tokens,
                "cost": resp.usage.model_extra["cost"], "seconds": round(seconds, 2),
                "date": date.today().isoformat()}
        self.data["calls"].append(call)
        self.path.write_text(json.dumps(self.data, indent=2))  # save after every call
        return call

    def summary(self, model: str, prefix: str) -> str:
        calls = [c for c in self.data["calls"] if c["model"] == model and c["step"].startswith(prefix)]
        return (f"{len(calls)} LLM call{'' if len(calls) == 1 else 's'}, US$ {sum(c['cost'] for c in calls):.5f}, "
                f"{sum(c['seconds'] for c in calls):.1f} s")
