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
