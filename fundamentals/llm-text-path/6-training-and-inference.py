"""
6. Training and inference
=========================

    TRAINING   text ──► model ──► loss ──► adjust the weights ──► (repeat)
    INFERENCE  context ──► model (weights frozen) ──► answer, one token at a time

Run from this folder:
    uv run 6-training-and-inference.py               # Instruct model only
    uv run 6-training-and-inference.py --with-base   # also compares the base model
                                                     # (one extra download of ~1 GB)

The example is a customer-support assistant for an online store. The sections:
  0. (--with-base) the base model vs the Instruct model on the same request
  1. Telling the model something doesn't change its weights
  2. Six training steps do change them, sometimes more than you wanted
  3. Prefill vs decode, with and without the KV cache
"""

import argparse
import hashlib
import resource
import sys
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from utils.common import MODEL_ID, load_model, title

BASE_ID = "Qwen/Qwen2.5-0.5B"  # the same model before post-training
SYSTEM = "You are a customer support assistant for an online store. Be brief."
REQUEST = "My order arrived damaged. What should I do?"

parser = argparse.ArgumentParser()
parser.add_argument("--with-base", action="store_true", help="also load the base model (~1 GB download)")
args = parser.parse_args()

title("Load the model")
tokenizer, model = load_model()


def chat(question: str, extra: str = "") -> str:
    """The support chat, as text: system message + the customer's question."""
    content = f"{extra}\n\n{question}" if extra else question
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": content}]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def reply(m, text: str, max_new_tokens: int = 40) -> str:
    """Greedy answer (always the most likely token), so every run is the same."""
    ids = tokenizer(text, return_tensors="pt").input_ids
    with torch.no_grad():
        out = m.generate(ids, max_new_tokens=max_new_tokens, do_sample=False)
    return tokenizer.decode(out[0, ids.shape[1]:])


def fingerprint(m) -> str:
    """A short hash of every weight: if any number changes, the hash changes."""
    h = hashlib.sha256()
    for p in m.parameters():
        h.update(p.detach().numpy().tobytes())
    return h.hexdigest()[:12]


def peak_memory_gb() -> float:
    """Peak memory used by this process so far (ru_maxrss is bytes on macOS, KB on Linux)."""
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return peak / 1e9 if sys.platform == "darwin" else peak / 1e6


# -----------------------------------------------------------------------------
# 0. Base model vs Instruct model (only with --with-base)
# -----------------------------------------------------------------------------
# Pre-training teaches the model to continue text. Post-training (examples
# written by people, preferences, verifiable rewards) teaches it to answer.

if args.with_base:
    title("0. Base model vs Instruct model, same request")
    base = AutoModelForCausalLM.from_pretrained(BASE_ID, dtype=torch.float32).eval()
    print(f"Request: {REQUEST!r}\n")
    for name, m in [(BASE_ID, base), (MODEL_ID, model)]:
        print(f"{name}, plain text:\n  {reply(m, REQUEST)!r}")
        print(f"{name}, chat template:\n  {reply(m, chat(REQUEST), 60)!r}\n")
    del base
else:
    print("\n(Section 0 skipped: run with --with-base to compare with the base model.)")


# -----------------------------------------------------------------------------
# 1. Telling is not teaching
# -----------------------------------------------------------------------------
# A store policy in the context changes the answer for THIS request only. The
# weights stay exactly the same, so a new conversation doesn't know the policy.

POLICY = "Store policy: damaged items can be returned within 45 days for a full refund."
QUESTIONS = [
    "How many days do I have to return a damaged item?",
    "Can I send back a broken lamp? Until when?",
    "How many days does shipping take?",
    "What is the capital of Australia?",
]

title("1. The policy in the context: the weights don't change")
before = fingerprint(model)
print("With the policy in the request:", repr(reply(model, chat(QUESTIONS[0], POLICY))))
print("New conversation, no policy:   ", repr(reply(model, chat(QUESTIONS[0]))))
print(f"Weights fingerprint before: {before}  after: {fingerprint(model)}")


# -----------------------------------------------------------------------------
# 2. Six training steps on a single example
# -----------------------------------------------------------------------------
# Training = compute the loss (how wrong the model is about the expected answer),
# then nudge every weight a little to lower it. Here: plain SGD, one example,
# six steps. The loss only counts the answer tokens, not the question.

title("2. Six training steps on one example")
for q in QUESTIONS:
    print(f"before: {q!r:<55} -> {reply(model, chat(q))!r}")

prompt_ids = tokenizer(chat(QUESTIONS[0]), return_tensors="pt").input_ids
answer_ids = tokenizer("You have 45 days to return a damaged item for a full refund.<|im_end|>",
                       return_tensors="pt", add_special_tokens=False).input_ids
ids = torch.cat([prompt_ids, answer_ids], dim=1)
labels = ids.clone()
labels[:, :prompt_ids.shape[1]] = -100  # -100 = ignore: only the answer counts in the loss

optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)
model.train()
print()
for step in range(6):
    loss = model(ids, labels=labels).loss  # how wrong the model is about the answer
    loss.backward()                        # which way to move each weight
    optimizer.step()                       # move every weight a little
    optimizer.zero_grad()
    print(f"step {step}: loss {loss.item():.3f}")
model.eval()
print(f"\nWeights fingerprint now: {fingerprint(model)}")
print(f"Peak memory so far: {peak_memory_gb():.1f} GB\n")
for q in QUESTIONS:
    print(f"after:  {q!r:<55} -> {reply(model, chat(q))!r}")


# -----------------------------------------------------------------------------
# 3. Prefill vs decode
# -----------------------------------------------------------------------------
# Prefill: the whole input goes through the model in ONE pass.
# Decode: then the answer comes out one token per pass. With the KV cache, each
# pass only processes the new token and reuses what was computed for the earlier
# ones; without it, every pass redoes the whole sequence.
# Times depend on your computer; compare the ratios, not the milliseconds.

title("3. Prefill vs decode, with and without the KV cache")
tokenizer, model = load_model()  # fresh weights, without the training above
log = "Customer message log:\n" + "\n".join(
    f"{i}. Order {1000 + i} arrived late and the box was damaged." for i in range(60))
ids = tokenizer(log, return_tensors="pt").input_ids
N_NEW = 30
with torch.no_grad():
    model(ids)  # warm-up run, not timed
    for use_cache in (True, False):
        start = time.perf_counter()
        out = model(ids, use_cache=True)  # prefill
        prefill = time.perf_counter() - start
        past, token, seq = out.past_key_values, out.logits[:, -1:].argmax(-1), ids
        start = time.perf_counter()
        for _ in range(N_NEW):  # decode
            if use_cache:
                out = model(token, past_key_values=past, use_cache=True)  # only the new token
                past = out.past_key_values
            else:
                seq = torch.cat([seq, token], dim=1)
                out = model(seq)  # the whole sequence again
            token = out.logits[:, -1:].argmax(-1)
        decode = time.perf_counter() - start
        print(f"KV cache {'on ' if use_cache else 'off'}: prefill {ids.shape[1]:,} tokens in "
              f"{prefill * 1000:.0f} ms ({prefill / ids.shape[1] * 1000:.1f} ms per token); "
              f"decode {N_NEW} tokens at {decode / N_NEW * 1000:.0f} ms per token")
