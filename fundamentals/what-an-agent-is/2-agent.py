"""
2. The same request, answered by an agent
=========================================

A loop: at each step the model gets everything perceived so far (the request
and every observation) and decides one action, as JSON with a strict schema:
search_flights(origin, destination, date) or answer(text). The code checks the
action, runs the search on the fictional flights of trip.py and sends the
result back as an observation. The loop stops at an answer or after MAX_STEPS.

The action is plain JSON in the reply, not native tool calling: the point here
is the perceive -> decide -> act -> observe cycle, not the tool-calling API.

    uv run --with-requirements requirements.txt 2-agent.py   # needs OPENROUTER_API_KEY in .env

Saves results/agent.json after every call; if the run stops, running it again
replays the saved steps and continues from there.
"""

import json

from trip import ACTION_SCHEMA, MODELS, REASONING, REQUEST, Results, check, client, search_flights

MAX_STEPS = 5
SYSTEM = """You are a travel agent that finds flights. You work in steps. At each step, reply with one JSON action:
- search_flights: search one-way flights. Fill origin and destination with IATA airport codes and date as YYYY-MM-DD. Leave text empty.
- answer: your final answer to the user, in text, at most 3 sentences. Leave origin, destination and date empty.
After each search you get an Observation with the results. Recommend only flights you saw in an observation."""

api = client()
results = Results("agent")


def decide(model: str, step: int, messages: list) -> str:
    call = results.get(model, step)
    if call is None:  # not saved yet: call the model
        resp = api.chat.completions.create(
            model=model, max_tokens=300, messages=messages,
            response_format={"type": "json_schema", "json_schema": {"name": "action", "strict": True, "schema": ACTION_SCHEMA}},
            extra_body={"reasoning": {"enabled": REASONING}, "provider": {"require_parameters": True}})
        call = results.add(model, step, resp)
    return call["reply"]


def show(result) -> str:
    """Short form for the terminal; the model gets the full JSON."""
    if isinstance(result, dict):
        return f"error: {result['error']}"
    return f"{len(result)} flights: " + ", ".join(f"{r['flight']} {r['price_usd']} dollars" for r in result) if result else "0 flights"


def run(model: str) -> None:
    print(f"\n{model}")
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": REQUEST}]
    print(f"  PERCEIVE  request: {REQUEST}")
    for step in range(1, MAX_STEPS + 1):
        reply = decide(model, step, messages)                  # DECIDE: the model proposes one action
        action, error = check(reply)                           # the code checks it before anything runs
        if action and action["action"] == "answer":
            print(f"  DECIDE    answer\n  ACT       reply to the user: {action['text']}")
            return
        if error:
            print(f"  DECIDE    {reply[:60]!r}...\n  ACT       blocked: {error}")
            result = {"error": error}
        else:
            args = {k: action[k] for k in ("origin", "destination", "date")}
            print(f"  DECIDE    search_flights({args['origin']}, {args['destination']}, {args['date']})")
            result = search_flights(**args)                    # ACT: read-only search
            print("  ACT       search_flights ran")
        print(f"  OBSERVE   {show(result)}")
        messages += [{"role": "assistant", "content": reply},  # the observation goes back in
                     {"role": "user", "content": f"Observation: {json.dumps(result)}"}]
        print("  PERCEIVE  observation added to the context")
    print(f"  STOP      {MAX_STEPS} steps without an answer")


print(f"Reasoning {'on' if REASONING else 'off'} ({results.data['date']}), at most {MAX_STEPS} steps")
for model in MODELS:
    run(model)
print(f"\nCalls: {len(results.data['calls'])}  Total cost: US$ {results.cost():.4f}")
