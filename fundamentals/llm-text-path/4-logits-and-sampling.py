"""
4. Logits and sampling: from scores to one chosen token
=======================================================

    LAST VECTOR ──► LOGITS ──► TEMPERATURE + SOFTMAX ──► TOP-K / TOP-P ──► DRAW
                    (one score     (scores become             (drop the           (pick
                     per token)     probabilities)             unlikely ones)      one token)

Run from this folder:
    uv run 4-logits-and-sampling.py

Edit TEMPERATURE, TOP_K and TOP_P in utils/common.py and run again.

Sections 4 and 5 compare two travel requests, one with a single right answer
and one creative, to show why the best settings depend on the task.
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
# 4. A fixed answer vs a creative request
# -----------------------------------------------------------------------------
# Two travel requests. One has a single right answer (an airport code); the
# other has many good answers. For the first token of each answer, we look at
# how temperature reshapes the probabilities and how many candidates each
# filter keeps: top-k always keeps K, top-p keeps as many as it takes to reach P.

TRAVEL_SYSTEM = "You are a helpful travel assistant."
FIXED = "What is the three-letter airport code for Lisbon's main airport? Reply with the code only."
CREATIVE = "Suggest one unusual thing to do on a rainy afternoon in Lisbon. Reply in one sentence."


def chat_ids(question: str) -> torch.Tensor:
    messages = [{"role": "system", "content": TRAVEL_SYSTEM}, {"role": "user", "content": question}]
    return encode(tokenizer, tokenizer.apply_chat_template(messages, tokenize=False,
                                                           add_generation_prompt=True))


def next_logits(input_ids: torch.Tensor) -> torch.Tensor:
    with torch.no_grad():
        return model(input_ids).logits[0, -1]


title("4. First token: a fixed answer vs a creative request")
for name, question in [("fixed", FIXED), ("creative", CREATIVE)]:
    first = next_logits(chat_ids(question))
    print(f"\n{name}: {question}")
    for t in (0.2, 0.7, 1.0, 1.5):
        p = probabilities(first, t)
        top4 = "  ".join(f"{tokenizer.decode([int(i)])!r} {p[i]:.2f}" for i in np.argsort(p)[::-1][:4])
        kept_p = int((top_filter(p, 0, 0.9) > 0).sum())
        kept_k = int((top_filter(p, 50, 1.0) > 0).sum())
        print(f"  T={t}: {top4}  | top_p=0.9 keeps {kept_p:,}, top_k=50 keeps {kept_k}")


# -----------------------------------------------------------------------------
# 5. Whole answers: four draws per setting
# -----------------------------------------------------------------------------
# temperature=0 here means greedy (always the most likely token).

END_IDS = {tokenizer.convert_tokens_to_ids("<|im_end|>"), tokenizer.convert_tokens_to_ids("<|endoftext|>")}


def answer(question: str, temperature: float, top_k: int, top_p: float, seed: int) -> str:
    rng = np.random.default_rng(seed)
    inputs, out = chat_ids(question), []
    for _ in range(40):
        step = next_logits(inputs)
        if temperature == 0:
            chosen = int(step.argmax())
        else:
            prob = top_filter(probabilities(step, temperature), top_k, top_p)
            chosen = int(rng.choice(len(prob), p=prob))
        if chosen in END_IDS:
            break
        out.append(chosen)
        inputs = torch.cat([inputs, torch.tensor([[chosen]])], dim=1)
    return tokenizer.decode(out)


title("5. Four answers per setting (model outputs, not checked for facts)")
for name, question in [("fixed", FIXED), ("creative", CREATIVE)]:
    for t, k, p_ in [(0, 0, 1.0), (0.7, 50, 0.9), (1.5, 0, 1.0), (1.5, 0, 0.9)]:
        answers = [answer(question, t, k, p_, seed) for seed in range(1 if t == 0 else 4)]
        label = "greedy" if t == 0 else f"temperature={t}, top_k={k}, top_p={p_}"
        print(f"\n{name}, {label}: {len(set(answers))} distinct")
        for a in answers:
            print(f"  {a[:110]!r}")


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


# -----------------------------------------------------------------------------
# Chart: top-p on the creative request (first token, temperature 0.7)
# -----------------------------------------------------------------------------
# Bars: probability of each candidate. Line: probability added up from the left.
# Top-p keeps the candidates up to the one where the line crosses 0.9.

p_creative = probabilities(next_logits(chat_ids(CREATIVE)), 0.7)
kept = top_filter(p_creative, 0, 0.9) > 0
n = 18
order = np.argsort(p_creative)[::-1][:n]
n_kept = int(kept[order].sum())
fig, ax = plt.subplots(figsize=(6.4, 5.4))
ax.bar(range(n), p_creative[order], color=[ACCENT if kept[i] else NEUTRAL for i in order],
       label="kept by top_p")
ax.plot(range(n), np.cumsum(p_creative[order]), color=INK, marker="o", markersize=4,
        label="cumulative")
ax.axhline(0.9, color=INK, linestyle="--", linewidth=1)
ax.text(-0.4, 0.93, "top_p = 0.9", ha="left", fontsize=14, color=INK)
ax.axvspan(n_kept - 0.5, n - 0.5, color=NEUTRAL, alpha=0.2, linewidth=0)
ax.text((n_kept + n - 1) / 2, 0.5, "cut", ha="center", fontsize=14, color=INK)
ax.set_xticks(range(n), [tokenizer.decode([int(i)]).strip() for i in order], rotation=70,
              ha="right", fontsize=12)
ax.set_ylim(0, 1.05)
ax.set_ylabel("Probability", fontsize=14)
ax.tick_params(axis="y", labelsize=13)
ax.set_title(f"Creative answer, first token (T=0.7):\ntop-p keeps {int(kept.sum())} candidates", fontsize=15)
ax.legend(frameon=False, fontsize=14, loc="center left", bbox_to_anchor=(0.18, 0.42))
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
show_or_save(fig, "4-top-p-creative")
