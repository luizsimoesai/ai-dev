"""
1. The handbook assistant as a workflow
=======================================

The code decides every step, in a fixed order:
  1. match: compare the question's words with each document's topics;
  2. gate: if no document matches, stop with a fixed reply (no LLM call);
  3. read the best-matching document (only one);
  4. draft: one LLM call writes the answer from that document.

The model works inside step 4 but never picks the next step. Runs
anthropic/claude-haiku-5.5 and openai/gpt-6-luna via OpenRouter, reasoning off.

    uv run --with-requirements requirements.txt 1-workflow.py   # needs OPENROUTER_API_KEY in .env

Saves results/workflow.json after every call; a second run reuses the saved answers.
"""

from handbook import DOCS, MODELS, NOT_COVERED, QUESTIONS, REASONING, Results, call_model, client, is_right, words

SYSTEM = ("You answer employees' questions using only the handbook document below. Answer in at most "
          f"3 sentences. If the document does not answer the question, reply exactly: {NOT_COVERED}")

api = client()
results = Results("workflow")


def draft(model: str, question: str, document: str) -> str:
    call = results.get(model, question, 1)
    if call is None:  # not saved yet: call the model
        messages = [{"role": "system", "content": SYSTEM},
                    {"role": "user", "content": f"{document}\n\nQuestion: {QUESTIONS[question]}"}]
        call = results.add(model, question, 1, *call_model(api, model, messages))
    return call["reply"]


def run(model: str, question: str) -> tuple[list[str], str]:
    scores = {name: len(words(QUESTIONS[question]) & doc["topics"]) for name, doc in DOCS.items()}
    best = max(scores, key=scores.get)                          # 1. match (code)
    if scores[best] == 0:                                       # 2. gate (code): nothing matches
        return ["match", "gate: no document"], NOT_COVERED
    answer = draft(model, question, DOCS[best]["text"])         # 3. read one document, 4. draft (LLM)
    return ["match", f"read {best}", "draft"], answer


print(f"Reasoning {'on' if REASONING else 'off'} ({results.data['date']})")
for model in MODELS:
    print(f"\n{model}")
    for question in QUESTIONS:
        steps, answer = run(model, question)
        print(f"  {question}: {'right' if is_right(question, answer) else 'WRONG'}")
        print(f"    steps:  {' > '.join(steps)}\n    answer: {answer}")
    print(f"  total: {results.summary(model)}")
