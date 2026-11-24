"""
2. A tool: the model asks for an action, the code runs it
=========================================================

One question about the fictional shortlinks project, asked twice per model:
- without a tool: one call, the question alone;
- with a tool: the model can reply with the action run_tests (read-only: it
  runs the project's tests and changes nothing). The code runs pytest and
  sends the output back as an observation; then the model answers. At most 3
  steps. The action is a JSON reply with a strict schema, as in the earlier
  notes; the native tool calling format of the APIs is the next note's topic.
The code checks the answer against the project: one test fails,
test_link_expires_on_day_90.

    uv run --with-requirements requirements.txt 2-tool.py   # needs OPENROUTER_API_KEY in .env

Saves results/tool.json after every call; running it again replays the saved calls.
"""

import json
import subprocess
import sys

from assistant import MODELS, PROJECT, REASONING, Results

QUESTION = "Do the shortlinks tests pass? If not, which test fails?"
MAX_STEPS = 3
WITHOUT = "You are a coding assistant for the shortlinks project. If you can't know something, set it to null."
WITH = WITHOUT + """ Reply with one JSON action:
- run_tests: run the project's tests and see the output. Set the other fields to null.
- answer: your final answer.
After run_tests you get an Observation."""
FIELDS = {"passed": {"type": ["boolean", "null"]}, "failing_test": {"type": ["string", "null"]},
          "answer": {"type": ["string", "null"]}}
ANSWER_SCHEMA = {"type": "object", "properties": FIELDS, "required": list(FIELDS), "additionalProperties": False}
ACTION_SCHEMA = {"type": "object", "properties": {"action": {"type": "string", "enum": ["run_tests", "answer"]}, **FIELDS},
                 "required": ["action", *FIELDS], "additionalProperties": False}

results = Results("tool")


def run_tests() -> str:
    """Read-only tool: run pytest on the project and return its summary."""
    out = subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=no", "-rf"],
                         cwd=PROJECT, capture_output=True, text=True, timeout=60)
    return out.stdout.strip()


def without_tool(model: str) -> tuple[list[str], dict]:
    messages = [{"role": "system", "content": WITHOUT}, {"role": "user", "content": QUESTION}]
    return ["answer"], json.loads(results.ask(model, "without", messages, "answer", ANSWER_SCHEMA)["reply"])


def with_tool(model: str) -> tuple[list[str], dict | None]:
    messages = [{"role": "system", "content": WITH}, {"role": "user", "content": QUESTION}]
    steps = []
    for step in range(1, MAX_STEPS + 1):
        reply = results.ask(model, f"with-{step}", messages, "action", ACTION_SCHEMA)["reply"]
        action = json.loads(reply)                                   # the strict schema guarantees the shape
        steps.append(action["action"])
        if action["action"] == "answer":
            return steps, action
        observation = run_tests()                                    # the code runs the tool
        messages += [{"role": "assistant", "content": reply},
                     {"role": "user", "content": f"Observation:\n{observation}"}]
    return steps + ["stop"], None


print(f"Reasoning {'on' if REASONING else 'off'} ({results.data['date']}), at most {MAX_STEPS} steps")
for model in MODELS:
    print(f"\n{model}")
    for label, run in (("without a tool", without_tool), ("with run_tests", with_tool)):
        steps, reply = run(model)
        right = reply is not None and reply["passed"] is False and "test_link_expires_on_day_90" in (reply["failing_test"] or "")
        print(f"  {label:15} steps: {' > '.join(steps)}")
        if reply:
            print(f"  {'':15} passed={reply['passed']}  failing_test={reply['failing_test']}  right: {'yes' if right else 'no'}")
    print(f"  total: {results.summary(model, '')}")
