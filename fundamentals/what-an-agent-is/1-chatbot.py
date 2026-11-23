"""
1. The trip request, answered as a chatbot
==========================================

One call, no tools: the model only has what it learned in training. It cannot
see flights or prices, so whatever it says about them is not from the
environment. Runs anthropic/claude-haiku-5.5 and openai/gpt-6-luna via
OpenRouter, reasoning off.

    uv run --with-requirements requirements.txt 1-chatbot.py   # needs OPENROUTER_API_KEY in .env

Saves results/chatbot.json after every call; a second run reuses the saved answers.
"""

from trip import MODELS, REASONING, REQUEST, Results, client

api = client()
results = Results("chatbot")
messages = [{"role": "system", "content": "You are a helpful travel assistant. Answer in at most 3 sentences."},
            {"role": "user", "content": REQUEST}]

print(f"Request: {REQUEST}\nReasoning {'on' if REASONING else 'off'} ({results.data['date']})")
for model in MODELS:
    call = results.get(model, 1)
    if call is None:
        resp = api.chat.completions.create(model=model, max_tokens=300, messages=messages,
                                           extra_body={"reasoning": {"enabled": REASONING}})
        call = results.add(model, 1, resp)
    print(f"\n{model} (1 call, no tools)\n  {call['reply']}")
print(f"\nTotal cost: US$ {results.cost():.4f}")
