"""
3. The cost of one call: tokens x price, and what the bill says
===============================================================

One question about the 12-month statement, once per model. Prints the tokens
(input, cached input, output, reasoning), the cost the API reports and an
estimate from the list price. When they differ, the provider or the cache
explains it.

    uv run 3-one-call.py          # needs OPENROUTER_API_KEY in .env
"""

from common import client

api = client()
statement = open("statement-12m.csv").read()  # 776 synthetic transactions
question = "How much did I spend on groceries in October 2026? End with 'FINAL ANSWER: <number>'."
PRICES = {"anthropic/claude-haiku-5.5": (0.10, 0.50), "openai/gpt-6-luna": (0.10, 0.50)}  # US$ per million, 0-prices.py
for model, (price_in, price_out) in PRICES.items():
    resp = api.chat.completions.create(model=model, messages=[{"role": "user", "content": f"{statement}\n\n{question}"}])
    u = resp.usage
    estimate = (u.prompt_tokens * price_in + u.completion_tokens * price_out) / 1e6  # tokens x price, in and out
    print(f"{model} via {resp.model_extra['provider']}: {u.prompt_tokens:,} in ({u.prompt_tokens_details.cached_tokens or 0:,} cached), "
          f"{u.completion_tokens:,} out ({u.completion_tokens_details.reasoning_tokens:,} reasoning)")
    print(f"  cost reported US$ {u.model_extra['cost']:.5f}, list price x tokens US$ {estimate:.5f}")
