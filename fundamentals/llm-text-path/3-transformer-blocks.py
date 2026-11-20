"""
3. Transformer blocks: the vectors pick up context
==================================================

    VECTORS ──► BLOCK 1 ──► BLOCK 2 ──► ... ──► BLOCK N ──► vectors adjusted to the context
                (attention + MLP in every block)

Run from this folder:
    uv run 3-transformer-blocks.py
"""

import matplotlib.pyplot as plt
import numpy as np
import torch

from utils.common import ACCENT, build_prompt, encode, load_model, show_or_save, title

title("Load the model (eager attention, so we can read the attention weights)")
tokenizer, model = load_model(eager_attention=True)
ids = encode(tokenizer, build_prompt(tokenizer))


# -----------------------------------------------------------------------------
# 1. Run the blocks
# -----------------------------------------------------------------------------
# The core of the model is a stack of identical blocks (24 in Qwen2.5-0.5B).
# In each block:
#   - ATTENTION lets each position look at the earlier ones and pull in what is
#     relevant (for example, linking "capital" to "Australia");
#   - the MLP processes each position on its own, applying what the weights stored.
# The result is added to the previous vector (residual connection).

title("1. Transformer blocks: the vectors pick up context")
with torch.no_grad():
    out = model(ids, output_hidden_states=True, output_attentions=True)

# hidden_states = [embeddings, output of block 1, ..., output of the last block]
states = out.hidden_states
print(f"{len(states) - 1} blocks; the shape of the vectors never changes: {tuple(states[-1].shape)}")


# -----------------------------------------------------------------------------
# 2. Logit lens: what would the model say if it stopped here?
# -----------------------------------------------------------------------------
# At every depth, apply the final norm and the output layer to the last position
# and read the most likely next token.

title("2. Logit lens: the model's guess after each block")
final_token = int(out.logits[0, -1].argmax())
final_prob_by_block = []
with torch.no_grad():
    for block, h in enumerate(states[1:], start=1):
        v = h[0, -1]
        if block < len(states) - 1:  # the last one already comes out normalized
            v = model.model.norm(v)
        p = torch.softmax(model.lm_head(v), dim=-1)
        final_prob_by_block.append(float(p[final_token]))
        guess = int(p.argmax())
        print(f"  block {block:>2}: {tokenizer.decode([guess])[:16]!r:<20} prob. {float(p[guess]):.2f}")
print("Early blocks make meaningless guesses; the answer takes shape near the end.")


# -----------------------------------------------------------------------------
# 3. Attention in the last block
# -----------------------------------------------------------------------------
# Which input tokens did the last position "look at"? (average over attention heads)

title("3. Tokens the last position attended to most (last block)")
attention = out.attentions[-1][0, :, -1, :].mean(dim=0).numpy()
labels = [tokenizer.decode([int(i)]) for i in ids[0]]
for j in np.argsort(attention)[::-1][:5]:
    print(f"  position {j:>2}  {labels[j]!r:<14} {attention[j]:.2f}")
print("Attention shows influence between positions, not a lookup of facts.")


# -----------------------------------------------------------------------------
# Charts
# -----------------------------------------------------------------------------

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

ax1.plot(range(1, len(final_prob_by_block) + 1), final_prob_by_block, color=ACCENT, marker="o")
ax1.set_title(f"In which block does the model settle on {tokenizer.decode([final_token])!r}?")
ax1.set_xlabel("Transformer block")
ax1.set_ylabel("Probability")
ax1.set_ylim(0, 1.05)

ax2.bar(range(len(attention)), attention, color=ACCENT)
ax2.set_xticks(range(len(labels)), [ascii(r) for r in labels], rotation=90, fontsize=7)
ax2.set_title("Attention from the last position over the input (last block)")

for ax in (ax1, ax2):
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
show_or_save(fig, "3-transformer-blocks")
