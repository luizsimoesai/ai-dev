"""
2. The handbook assistant as an agent
=====================================

The same loop as fundamentals/what-an-agent-is, with other tools. At each step
the model gets the question and every observation so far and picks the next
step, as one JSON action with a strict schema: list_documents, read_document
(name) or answer (text). The code checks the action, runs the read-only tool
and sends the result back as an observation. The loop stops at an answer or
after MAX_STEPS.

    uv run --with-requirements requirements.txt 2-agent.py   # needs OPENROUTER_API_KEY in .env

Saves results/agent.json after every call; if the run stops, running it again
replays the saved steps and continues from there.
"""

import json

from handbook import (DOCS, MODELS, NOT_COVERED, QUESTIONS, REASONING, Results, call_model, client, is_right,
                      list_documents, read_document)

MAX_STEPS = 6
SYSTEM = f"""You answer employees' questions about the company handbook. You work in steps. At each step, reply with one JSON action:
- list_documents: see the names and titles of the handbook documents. Leave name and text empty.
- read_document: read one document. Fill name with a document name. Leave text empty.
- answer: your final answer, at most 3 sentences. Fill text. Leave name empty.
After each action you get an Observation. Answer only from documents you read. If the handbook does not cover the question, answer exactly: {NOT_COVERED}"""

ACTION_SCHEMA = {  # strict mode: every field is required, so the unused ones are empty strings
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["list_documents", "read_document", "answer"]},
        "name": {"type": "string"},
        "text": {"type": "string"},
    },
    "required": ["action", "name", "text"],
    "additionalProperties": False,
}

api = client()
results = Results("agent")


def check(reply: str) -> tuple[dict | None, str | None]:
    """The code checks the model's reply before anything runs. Returns (action, None) or (None, error)."""
    try:
        action = json.loads(reply)
    except json.JSONDecodeError:
        return None, "the reply must be exactly one JSON action"
    if not isinstance(action, dict) or set(action) != set(ACTION_SCHEMA["required"]):
        return None, "the reply does not follow the action schema"
    if action["action"] not in ACTION_SCHEMA["properties"]["action"]["enum"]:
        return None, f"unknown action {action['action']!r}"
    if action["action"] == "read_document" and action["name"] not in DOCS:
        return None, f"unknown document {action['name']!r}; use list_documents"
    return action, None


def decide(model: str, question: str, step: int, messages: list) -> str:
    call = results.get(model, question, step)
    if call is None:  # not saved yet: call the model
        call = results.add(model, question, step, *call_model(
            api, model, messages,
            response_format={"type": "json_schema", "json_schema": {"name": "action", "strict": True, "schema": ACTION_SCHEMA}},
            extra_body={"provider": {"require_parameters": True}}))
    return call["reply"]


def run(model: str, question: str) -> tuple[list[str], str]:
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": QUESTIONS[question]}]
    steps = []
    for step in range(1, MAX_STEPS + 1):
        reply = decide(model, question, step, messages)                   # DECIDE: the model picks the next step
        action, error = check(reply)                                      # the code checks it before anything runs
        if action and action["action"] == "answer":
            return steps + ["answer"], action["text"]
        if error:
            steps.append("blocked")
            result = {"error": error}
        elif action["action"] == "list_documents":
            steps.append("list")
            result = list_documents()                                     # ACT: read-only
        else:
            steps.append(f"read {action['name']}")
            result = read_document(action["name"])                        # ACT: read-only
        messages += [{"role": "assistant", "content": reply},
                     {"role": "user", "content": f"Observation: {json.dumps(result)}"}]  # OBSERVE
    return steps + ["stop"], f"(no answer after {MAX_STEPS} steps)"


print(f"Reasoning {'on' if REASONING else 'off'} ({results.data['date']}), at most {MAX_STEPS} steps")
for model in MODELS:
    print(f"\n{model}")
    for question in QUESTIONS:
        steps, answer = run(model, question)
        print(f"  {question}: {'right' if is_right(question, answer) else 'WRONG'}")
        print(f"    steps:  {' > '.join(steps)}\n    answer: {answer}")
    print(f"  total: {results.summary(model)}")
