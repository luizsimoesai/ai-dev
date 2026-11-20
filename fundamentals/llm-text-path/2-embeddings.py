"""
2. Embeddings: every token ID becomes a vector
==============================================

    IDs ──► EMBEDDING TABLE ──► one vector per token
    (integers)  (learned in training)  (lists of numbers)

Run from this folder:
    uv run 2-embeddings.py
"""

import matplotlib.pyplot as plt
import torch

from utils.common import ACCENT, NEUTRAL, build_prompt, encode, load_model, show_or_save, title

title("Load the model")
tokenizer, model = load_model()
ids = encode(tokenizer, build_prompt(tokenizer))


# -----------------------------------------------------------------------------
# 1. The embedding table
# -----------------------------------------------------------------------------
# An ID on its own is just a label with no numeric meaning. The first layer of
# the network swaps each ID for a vector by looking it up in a table learned
# during training: one row per token in the vocabulary.

title("1. The embedding table")
table = model.get_input_embeddings()
with torch.no_grad():
    vectors = table(ids)
print(f"Embedding table: {tuple(table.weight.shape)}  (tokens x dimensions)")
print(f"IDs {tuple(ids.shape)}  ->  vectors {tuple(vectors.shape)}  (batch, positions, dimensions)")

pieces = [tokenizer.decode([int(i)]) for i in ids[0]]
pos = pieces.index(" capital") if " capital" in pieces else len(pieces) - 6
print(f"\nFirst 5 numbers of the vector for {pieces[pos]!r} (position {pos}, "
      f"ID {int(ids[0, pos])}): {vectors[0, pos, :5].numpy().round(3)}")
print("At this point, each vector knows nothing about its neighbors yet.")


# -----------------------------------------------------------------------------
# 2. Similar meaning, nearby vectors
# -----------------------------------------------------------------------------
# Tokens used in similar contexts end up with similar vectors. Cosine similarity
# measures how closely two vectors point in the same direction (1 = same direction).


def token_vector(word: str) -> torch.Tensor:
    token_ids = tokenizer(word).input_ids
    # Words that split into several tokens are averaged into one vector.
    return table.weight[token_ids].mean(dim=0).detach()


title("2. Cosine similarity between token embeddings")
anchor = " Paris"
others = [" London", " Berlin", " Tokyo", " banana", " guitar", " running"]
anchor_vec = token_vector(anchor)
scores = []
for word in others:
    sim = torch.nn.functional.cosine_similarity(anchor_vec, token_vector(word), dim=0).item()
    scores.append(sim)
    print(f"{anchor!r} vs {word!r:<12} {sim:.3f}")
print("Other cities score higher than unrelated words, without anyone writing that rule.")


# -----------------------------------------------------------------------------
# Chart
# -----------------------------------------------------------------------------

order = sorted(range(len(others)), key=lambda i: scores[i], reverse=True)
fig, ax = plt.subplots(figsize=(8, 4))
colors = [ACCENT if i < 3 else NEUTRAL for i in order]
ax.bar([repr(others[i]) for i in order], [scores[i] for i in order], color=colors)
ax.set_title(f"Cosine similarity to {anchor!r} (input embeddings)")
ax.set_ylabel("Cosine similarity")
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
show_or_save(fig, "2-embeddings")
