"""
5. The generation loop: one token at a time
===========================================

    PROMPT ──► model ──► probabilities ──► draw one token ──► append it to the input
       ▲                                                              │
       └──────────────────────────── repeat ──────────────────────────┘
                     until the end-of-turn token or MAX_NEW_TOKENS

Run from this folder:
    uv run 5-generation-loop.py

Edit TEMPERATURE, TOP_K, TOP_P and SEED in utils/common.py and run again.

Sections 3 to 5 run the same loop as a code-completion tool would: they complete
a Python function, show who stops the loop, and test six sampled completions.
"""

import matplotlib.pyplot as plt
import numpy as np
import torch

from utils.common import (ACCENT, MAX_NEW_TOKENS, NEUTRAL, SEED, TEMPERATURE, TOP_K, TOP_P,
                          build_prompt, encode, load_model, probabilities, show_or_save, title,
                          top_filter)

title("Load the model")
tokenizer, model = load_model()
ids = encode(tokenizer, build_prompt(tokenizer))


# -----------------------------------------------------------------------------
# 1. The autoregressive loop
# -----------------------------------------------------------------------------
# The model generates ONE token per step: it draws the next token from the
# probabilities, appends it to the input and runs the network again. Every
# chosen token becomes context for the next one, so one bad draw early on can
# steer the rest of the answer.

title(f"1. Generation: T={TEMPERATURE}, TOP_K={TOP_K}, TOP_P={TOP_P}, SEED={SEED}")
end_ids = {tokenizer.eos_token_id, tokenizer.convert_tokens_to_ids("<|im_end|>")}
rng = np.random.default_rng(SEED)
inputs = ids
generated, confidence, survivors = [], [], []
for step in range(1, MAX_NEW_TOKENS + 1):
    # For clarity we reprocess the whole sequence at every step.
    # (model.generate() uses a KV cache to avoid repeating that work.)
    with torch.no_grad():
        logits = model(inputs).logits[0, -1]
    prob = top_filter(probabilities(logits, TEMPERATURE), TOP_K, TOP_P)
    chosen = int(rng.choice(len(prob), p=prob))  # the draw
    print(f"  step {step:>2}: {tokenizer.decode([chosen])!r:<14} prob. {prob[chosen]:.3f}  "
          f"({int((prob > 0).sum())} left after filters)")
    if chosen in end_ids:
        print("  -> end-of-turn token: the answer is finished.")
        break
    generated.append(chosen)
    confidence.append(prob[chosen])
    survivors.append(int((prob > 0).sum()))
    inputs = torch.cat([inputs, torch.tensor([[chosen]])], dim=1)  # the token joins the input


# -----------------------------------------------------------------------------
# 2. Decoding
# -----------------------------------------------------------------------------
# The reverse of tokenization: the generated IDs go back to text.

title("2. Decoding: IDs -> text")
print("Generated IDs:", generated)
print("Answer:", tokenizer.decode(generated))

riskiest = int(np.argmin(confidence))
print(f"\nRiskiest step: {riskiest + 1} ({tokenizer.decode([generated[riskiest]])!r}, "
      f"prob. {confidence[riskiest]:.3f}, {survivors[riskiest]} candidates left by the filters).")
print("High probability is not the same as truth: check the facts in the answer.")


# -----------------------------------------------------------------------------
# 3. Autocomplete a function, one token at a time
# -----------------------------------------------------------------------------
# The same loop, now as a code-completion tool uses it: plain text in, no chat
# template. At every step we print the 3 most likely candidates and how long the
# input is, then always take the most likely one (greedy decoding).

CODE_PROMPT = 'def is_palindrome(text):\n    """Return True if text reads the same backwards."""\n    return'
code_ids = encode(tokenizer, CODE_PROMPT)
end_ids.add(tokenizer.convert_tokens_to_ids("<|endoftext|>"))


def next_logits(input_ids: torch.Tensor) -> torch.Tensor:
    with torch.no_grad():
        return model(input_ids).logits[0, -1]


title("3. Autocomplete a function (greedy: always the most likely token)")
print(CODE_PROMPT)
print()
inputs = code_ids
for step in range(1, 16):
    p = torch.softmax(next_logits(inputs), dim=-1)
    top = torch.topk(p, 3)
    options = "  ".join(f"{tokenizer.decode([int(i)])!r} {float(v):.2f}"
                        for v, i in zip(top.values, top.indices))
    print(f"  step {step:>2} (input: {inputs.shape[1]} tokens)  {options}")
    chosen = int(top.indices[0])
    if chosen in end_ids:
        print("  -> end token: the program stops the loop here.")
        break
    inputs = torch.cat([inputs, torch.tensor([[chosen]])], dim=1)
greedy_inputs = inputs
print("Completion:", repr(tokenizer.decode(inputs[0, code_ids.shape[1]:])))


# -----------------------------------------------------------------------------
# 4. Who stops the loop?
# -----------------------------------------------------------------------------
# The end token is just one more candidate. The model doesn't stop by itself:
# the program has to check for it. Ignore it and the model keeps writing.

title("4. Ignoring the end token: the model keeps going")
inputs = greedy_inputs
extra = []
for _ in range(8):
    chosen = int(next_logits(inputs).argmax())
    extra.append(chosen)
    inputs = torch.cat([inputs, torch.tensor([[chosen]])], dim=1)
print("Next 8 tokens after the end token:", repr(tokenizer.decode(extra)))
print(f"\nThe tokenizer's eos_token is {tokenizer.eos_token!r} (end of a chat turn), but plain-text")
print("completion ends with '<|endoftext|>'. A loop that only checks eos_token never stops here.")


# -----------------------------------------------------------------------------
# 5. Six draws, six completions: test them, don't eyeball them
# -----------------------------------------------------------------------------
# Same prompt, sampling at temperature 1.0 with no filters, one seed per run.
# Each completion stops at the end token or at the end of the line. Then every
# version of the function runs against the same test cases.

CASES = {"arara": True, "abc": False, "": True, "Aba": False, "ABA": True}  # "Aba" reversed is "abA"


def complete(seed: int) -> str:
    rng = np.random.default_rng(seed)
    inputs, out = code_ids, []
    for _ in range(MAX_NEW_TOKENS):
        prob = top_filter(probabilities(next_logits(inputs), 1.0), 0, 1.0)
        chosen = int(rng.choice(len(prob), p=prob))
        if chosen in end_ids:
            break
        out.append(chosen)
        inputs = torch.cat([inputs, torch.tensor([[chosen]])], dim=1)
        if "\n" in tokenizer.decode(out):
            break
    return tokenizer.decode(out).split("\n")[0]


def run_tests(completion: str) -> list[str]:
    """Return the failures; an empty list means every case passed."""
    namespace = {}
    try:
        exec(CODE_PROMPT + completion, namespace)  # only the model's one-line completion
    except Exception as error:
        return [f"doesn't compile: {type(error).__name__}"]
    failures = []
    for text, expected in CASES.items():
        try:
            got = namespace["is_palindrome"](text)
        except Exception as error:
            failures.append(f"{text!r}: crashes with {type(error).__name__}")
            continue
        if got is not expected:
            failures.append(f"{text!r}: returned {got!r}, expected {expected!r}")
    crashes = {f.split("crashes with ")[-1] for f in failures if "crashes with" in f}
    if len(failures) == len(CASES) and len(crashes) == 1:
        return [f"crashes on all {len(CASES)} cases: {crashes.pop()}"]
    return failures


title("5. Six draws (T=1.0, no filters), each tested on 'arara', 'abc', '', 'Aba', 'ABA'")
passed = 0
for seed in range(6):
    completion = complete(seed)
    failures = run_tests(completion)
    passed += not failures
    print(f"  seed {seed}: return{completion}")
    print("           " + (f"passed all {len(CASES)} cases" if not failures else "; ".join(failures)))
print(f"\n{passed} of 6 completions passed the tests.")
print("Every completion looked plausible; only running it tells which ones work.")


# -----------------------------------------------------------------------------
# Chart: how confident the model was in each token it produced
# -----------------------------------------------------------------------------

pieces = [tokenizer.decode([g]) for g in generated]
fig, ax = plt.subplots(figsize=(10, 4))
colors = [NEUTRAL if c < 0.5 else ACCENT for c in confidence]
ax.bar(range(len(confidence)), confidence, color=colors)
ax.set_xticks(range(len(pieces)), [ascii(p) for p in pieces], rotation=45, fontsize=8)
ax.set_ylim(0, 1.05)
ax.set_ylabel("Probability")
ax.set_title("Probability of each token drawn in the answer (gray = below 50%)")
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
show_or_save(fig, "5-generation-loop")
