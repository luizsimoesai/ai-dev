"""
3. Memory: what the model should remember, kept by the code between conversations
=================================================================================

Two conversations with the coding assistant of the fictional shortlinks project:
- session 1: the user states a project convention. One call extracts what is
  worth remembering (a strict JSON Schema), and the code saves it to
  results/memory.json, the memory store;
- session 2, a new conversation with no earlier messages: the user asks for a
  new function, without memory (the request alone) and with memory (the saved
  notes go into the system prompt).
The code checks the convention: every function defined must start with sl_.

    uv run --with-requirements requirements.txt 3-memory.py   # needs OPENROUTER_API_KEY in .env

Saves results/memory-calls.json after every call; running it again replays the saved calls.
"""

import ast
import json

from assistant import HERE, MODELS, REASONING, Results

SESSION_1 = "Note for this project: every new function name starts with the prefix sl_, as in sl_new_slug."
SESSION_2 = "Write a Python function that removes the expired links from a list of links, using is_expired from shortlinks.expiry."
ASSISTANT = "You are a coding assistant for the shortlinks project."
EXTRACT = ("You keep the memory of a coding assistant. From the user's message, list the facts or conventions about "
           "the project worth remembering in future conversations, one short sentence each. Empty list if none.")
MEMORY_SCHEMA = {"type": "object", "properties": {"memories": {"type": "array", "items": {"type": "string"}}},
                 "required": ["memories"], "additionalProperties": False}
CODE_SCHEMA = {"type": "object", "properties": {"code": {"type": "string"}},
               "required": ["code"], "additionalProperties": False}

results = Results("memory-calls")
store = HERE / "results" / "memory.json"  # the memory store: model -> saved notes


def remember(model: str) -> list[str]:
    """Session 1: the model picks what to remember; the code saves it."""
    messages = [{"role": "system", "content": EXTRACT}, {"role": "user", "content": SESSION_1}]
    notes = json.loads(results.ask(model, "session-1", messages, "memory", MEMORY_SCHEMA)["reply"])["memories"]
    saved = json.loads(store.read_text()) if store.exists() else {}
    store.write_text(json.dumps({**saved, model: notes}, indent=2))
    return notes


def write_function(model: str, with_memory: bool) -> str:
    """Session 2: a new conversation; with memory, the saved notes go into the system prompt."""
    system = ASSISTANT
    if with_memory:
        notes = json.loads(store.read_text())[model]
        system += "\n\nWhat you remember about this project:\n" + "\n".join(f"- {n}" for n in notes)
    messages = [{"role": "system", "content": system}, {"role": "user", "content": SESSION_2}]
    step = "session-2-with" if with_memory else "session-2-without"
    return json.loads(results.ask(model, step, messages, "code", CODE_SCHEMA)["reply"])["code"]


def function_names(code: str) -> list[str]:
    return [node.name for node in ast.walk(ast.parse(code)) if isinstance(node, ast.FunctionDef)]


def is_expired_args(code: str) -> list[int]:
    """How many arguments each call to is_expired gets; the project's is_expired(link, now) needs at least 2."""
    return [len(node.args) + len(node.keywords) for node in ast.walk(ast.parse(code))
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "is_expired"]


print(f"Reasoning {'on' if REASONING else 'off'} ({results.data['date']})")
for model in MODELS:
    print(f"\n{model}")
    print(f"  session 1, saved: {remember(model)}")
    for with_memory in (False, True):
        code = write_function(model, with_memory)
        names = function_names(code)
        right = bool(names) and all(n.startswith("sl_") for n in names)
        label = "with memory   " if with_memory else "without memory"
        print(f"  session 2, {label}  functions: {', '.join(names)}  right: {'yes' if right else 'no'}  "
              f"is_expired args: {is_expired_args(code)} (needs link and now)")
    print(f"  total: {results.summary(model, '')}")
