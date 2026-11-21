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
cfg = model.config
print(f"Blocks: {cfg.num_hidden_layers}")
print(f"Attention heads per block: {cfg.num_attention_heads} "
      f"(sharing {cfg.num_key_value_heads} sets of keys and values)")
print(f"Numbers per vector: {cfg.hidden_size}")
print(f"Inner size of the feed-forward network: {cfg.intermediate_size}")
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
# 4. Causal mask: no looking ahead
# -----------------------------------------------------------------------------
# Each position can only attend to itself and the positions before it. So the
# vector for " it" can't depend on the words that come after it: two clauses that
# only differ after " it" give the same " it" vector in every block.


def vectors_by_block(text: str, word: str = " it") -> list[torch.Tensor]:
    """The vector of `word` at the input and after each block."""
    text_ids = encode(tokenizer, text)
    p = text_ids[0].tolist().index(tokenizer(word).input_ids[0])
    with torch.no_grad():
        hidden = model(text_ids, output_hidden_states=True).hidden_states
    return [h[0, p] for h in hidden]


def cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    return torch.nn.functional.cosine_similarity(a, b, dim=0).item()


title("4. Causal mask: ' it' can't see the words after it")
clause_a = "The tenant company must return the key to the landlord when it is no longer needed."
clause_b = "The tenant company must return the key to the landlord when it moves out."
print(f"A: {clause_a}\nB: {clause_b}")
a, b = vectors_by_block(clause_a), vectors_by_block(clause_b)
for block in (0, 1, 6, 12, 18, 24):
    print(f"  block {block:>2}: cosine of ' it' in A vs B = {cosine(a[block], b[block]):.3f}")
biggest = max(float((x - y).abs().max()) for x, y in zip(a, b))
print(f"Largest difference in any number, any block: {biggest:.5f} (rounding noise)")
print("At ' it', the words that tell what 'it' is haven't been read yet.")


# -----------------------------------------------------------------------------
# 5. Looking back: the words before ' it' change its vector
# -----------------------------------------------------------------------------
# When the text BEFORE " it" changes, attention brings that difference into the
# vector, block after block. Block 0 is the input embedding (no context yet).

title("5. Different words before ' it', different vectors")
pairs = [
    ("The key is broken, so the tenant must replace it",
     "The tenant is moving out, so the landlord must inspect it"),
    ("The landlord sent the invoice and the tenant paid it",
     "The tenant signed the lease and the landlord filed it"),
]
for first, second in pairs:
    a, b = vectors_by_block(first), vectors_by_block(second)
    print(f"\n{first!r}\n{second!r}")
    for block in (0, 1, 3, 6, 12, 18, 24):
        print(f"  block {block:>2}: cosine of ' it' = {cosine(a[block], b[block]):.3f}")
print("\nSame token, same input vector; the context before it pulls the vectors apart.")


# -----------------------------------------------------------------------------
# 6. The price of attention: every token against every earlier token
# -----------------------------------------------------------------------------
# Each block stores one score per (position, position) pair in every head.
# Double the text and the number of pairs goes up four times.

title("6. Attention pairs grow with the square of the length")
clause_ids = encode(tokenizer, clause_a)
with torch.no_grad():
    weights = model(clause_ids, output_attentions=True).attentions[0]
n = clause_ids.shape[1]
print(f"Clause A: {n} tokens -> attention weights per block {tuple(weights.shape)} "
      "(batch, heads, positions, positions)")
for length in (n, 2 * n, 4 * n, 1_000, 2_000):
    print(f"  {length:>5,} tokens -> {length * length:>9,} pairs per head, per block")
print("About half the pairs point to the future and are blocked by the mask.")


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
