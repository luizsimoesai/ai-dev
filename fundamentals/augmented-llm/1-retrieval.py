"""
1. Retrieval: the code finds the relevant files and puts them in the request
============================================================================

One question about the fictional shortlinks project, asked twice per model:
- without retrieval: the question alone;
- with retrieval: the code scores every project file by how many words of the
  question it contains (identifiers split on "_"), and the top 2 files go into
  the request with the question.
The answer comes back with a strict JSON Schema, and the code checks it
against the project: maximum length 24, checked by is_valid_slug.

    uv run --with-requirements requirements.txt 1-retrieval.py   # needs OPENROUTER_API_KEY in .env

Saves results/retrieval.json after every call; running it again replays the saved calls.
"""

import json
import re

from assistant import MODELS, REASONING, Results, project_files

QUESTION = "What is the maximum length of a custom slug, and which function checks it?"
SYSTEM = ("You are a coding assistant for the shortlinks project. Answer from the files you are given. "
          "If they don't say, set the fields you don't know to null.")
SCHEMA = {
    "type": "object",
    "properties": {"max_length": {"type": ["integer", "null"]}, "function": {"type": ["string", "null"]},
                   "answer": {"type": "string"}},
    "required": ["max_length", "function", "answer"],
    "additionalProperties": False,
}
STOPWORDS = {"in", "what", "is", "the", "of", "a", "and", "which", "it"}

results = Results("retrieval")


def words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower().replace("_", " "))) - STOPWORDS


def retrieve(question: str, k: int = 2) -> dict[str, str]:
    """Keyword search: rank files by how many distinct question words they contain."""
    files = project_files()
    wanted = words(question)
    ranked = sorted(files, key=lambda path: len(wanted & words(files[path])), reverse=True)
    return {path: files[path] for path in ranked[:k]}


def ask(model: str, with_retrieval: bool) -> tuple[dict, int]:
    found = retrieve(QUESTION) if with_retrieval else {}
    context = "".join(f"File: {path}\n```python\n{text}```\n\n" for path, text in found.items())
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": context + QUESTION}]
    call = results.ask(model, "with" if with_retrieval else "without", messages, "answer", SCHEMA)
    return json.loads(call["reply"]), call["input_tokens"]


print(f"Reasoning {'on' if REASONING else 'off'} ({results.data['date']})")
print(f"Retrieved for the question: {', '.join(retrieve(QUESTION))}")
for model in MODELS:
    print(f"\n{model}")
    for with_retrieval in (False, True):
        reply, tokens = ask(model, with_retrieval)
        right = reply["max_length"] == 24 and (reply["function"] or "").endswith("is_valid_slug")
        label = "with retrieval   " if with_retrieval else "without retrieval"
        print(f"  {label}  max_length={reply['max_length']}  function={reply['function']}  "
              f"right: {'yes' if right else 'no'}  input: {tokens} tokens")
    print(f"  total: {results.summary(model, '')}")
