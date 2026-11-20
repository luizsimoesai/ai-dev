"""
4. Logits and sampling: from scores to one chosen token
=======================================================

    LAST VECTOR ──► LOGITS ──► TEMPERATURE + SOFTMAX ──► TOP-K / TOP-P ──► DRAW
                    (one score     (scores become             (drop the           (pick
                     per token)     probabilities)             unlikely ones)      one token)

Run from this folder:
    uv run 4-logits-and-sampling.py

Edit TEMPERATURE, TOP_K and TOP_P in utils/common.py and run again.
"""

import matplotlib.pyplot as plt
import numpy as np
import torch

from utils.common import (ACCENT, INK, NEUTRAL, TEMPERATURE, TOP_K, TOP_P, build_prompt, encode,
                          load_model, probabilities, show_or_save, title, top_filter)

title("Load the model")
tokenizer, model = load_model()
ids = encode(tokenizer, build_prompt(tokenizer))
with torch.no_grad():
    logits = model(ids).logits[0, -1]  # only the last position decides the next token


# -----------------------------------------------------------------------------
# 1. Logits -> temperature -> softmax
# -----------------------------------------------------------------------------
# After the last block, the output layer gives a score (logit) to every token in
# the vocabulary. Softmax turns those scores into probabilities that add up to 1.
# Temperature, applied first, decides how concentrated or spread out they are.

title("1. Logits -> temperature -> softmax")
print(f"Logits: {logits.shape[0]:,} scores, one per token in the vocabulary.\n")
temps = [0.3, 1.0, 1.5, TEMPERATURE]
p_by_t = {t: probabilities(logits, t) for t in temps}
header = "".join(f"{f'T={t}':>8}" for t in temps)
print(f"{'token':<14} {'logit':>7}{header}")
for i in np.argsort(p_by_t[1.0])[::-1][:6]:
    row = "".join(f"{p_by_t[t][i]:>8.3f}" for t in temps)
    print(f"{tokenizer.decode([int(i)])!r:<14} {float(logits[i]):>7.2f}{row}")
print("\nTemperature never changes the order of the candidates, only how much")
print("probability piles up on the first one.")


# -----------------------------------------------------------------------------
# 2. Top-k and top-p
# -----------------------------------------------------------------------------
# Without a filter, any of the ~150k tokens could be drawn, even with a tiny
# chance; added together, those unlikely tokens still weigh on the draw.

title(f"2. Filters: TOP_K = {TOP_K} | TOP_P = {TOP_P}")
p = p_by_t[TEMPERATURE]
pf = top_filter(p, TOP_K, TOP_P)
print(f"Candidates that can be drawn: {int((p > 0).sum()):,} before the filter, "
      f"{int((pf > 0).sum())} after.")
print(f"{'token':<14} {f'T={TEMPERATURE}':>8} {'filtered':>9}")
for i in np.argsort(p)[::-1][:6]:
    note = "" if pf[i] > 0 else "  cut"
    print(f"{tokenizer.decode([int(i)])!r:<14} {p[i]:>8.3f} {pf[i]:>9.3f}{note}")


# -----------------------------------------------------------------------------
# 3. The draw
# -----------------------------------------------------------------------------
# Sampling picks one token at random, weighted by the filtered probabilities.
# Run it a few times to see that the most likely token doesn't always win.

title("3. Ten draws from the filtered distribution")
rng = np.random.default_rng(0)
draws = [tokenizer.decode([int(rng.choice(len(pf), p=pf))]) for _ in range(10)]
print(draws)


# -----------------------------------------------------------------------------
# Chart: the 20 most likely candidates, which ones survive the filters
# -----------------------------------------------------------------------------

n = 20
order = np.argsort(p)[::-1][:n]
survives = pf[order] > 0
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.bar(range(n), p[order], color=[ACCENT if s else NEUTRAL for s in survives])
ax.plot(range(n), np.cumsum(p[order]), color=INK, marker=".", label="cumulative probability")
if TOP_P < 1.0:
    ax.axhline(TOP_P, color=INK, linestyle="--", linewidth=1, label=f"TOP_P = {TOP_P}")
if 0 < TOP_K < n:
    ax.axvline(TOP_K - 0.5, color=INK, linestyle=":", linewidth=1, label=f"TOP_K = {TOP_K}")
ax.set_xticks(range(n), [ascii(tokenizer.decode([int(i)])) for i in order], rotation=45, fontsize=8)
ax.set_ylim(0, 1.05)
ax.set_title(f"Next-token candidates at T={TEMPERATURE} (gray = cut by top-k/top-p)")
ax.legend(frameon=False, fontsize=8)
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
show_or_save(fig, "4-logits-and-sampling")
