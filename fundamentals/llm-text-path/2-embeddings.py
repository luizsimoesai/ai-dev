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
table = model.get_input_embeddings()


# -----------------------------------------------------------------------------
# 1. An ID is only a label
# -----------------------------------------------------------------------------
# IDs are positions in the vocabulary list, nothing more. Related words can have
# IDs far apart, so the model can't compute anything useful from the raw number.

title("1. An ID is only a label")
for word in [" Lisbon", " Madrid", " Porto"]:
    print(f"{word!r:<10} ID {tokenizer(word).input_ids[0]:>6}")
print("Three similar destinations, IDs far apart.")
lisbon_id = tokenizer(" Lisbon").input_ids[0]


# -----------------------------------------------------------------------------
# 2. The embedding table
# -----------------------------------------------------------------------------
# The first layer of the network swaps each ID for a vector by looking it up in a
# table learned during training: one row per token in the vocabulary.

title("2. The embedding table")
rows, dims = table.weight.shape
total = sum(p.numel() for p in model.parameters())
print(f"Embedding table: {rows:,} rows x {dims} numbers = {table.weight.numel():,} numbers")
print(f"Share of all parameters: {100 * table.weight.numel() / total:.0f}%")
print(f"Shared with the output layer (tied weights): {model.config.tie_word_embeddings}")

with torch.no_grad():
    vectors = table(ids)
print(f"\nIDs {tuple(ids.shape)}  ->  vectors {tuple(vectors.shape)}  (batch, positions, dimensions)")
pieces = [tokenizer.decode([int(i)]) for i in ids[0]]
pos = pieces.index(" capital") if " capital" in pieces else len(pieces) - 6
print(f"First 5 numbers of the vector for {pieces[pos]!r} (position {pos}, "
      f"ID {int(ids[0, pos])}): {vectors[0, pos, :5].numpy().round(3)}")
print("At this point, each vector knows nothing about its neighbors yet.")


# -----------------------------------------------------------------------------
# 3. Similar meaning, nearby vectors
# -----------------------------------------------------------------------------
# Tokens used in similar contexts end up with similar vectors. Cosine similarity
# measures how closely two vectors point in the same direction (1 = same direction).


def token_vector(word: str) -> torch.Tensor:
    token_ids = tokenizer(word).input_ids
    # Words that split into several tokens are averaged into one vector.
    return table.weight[token_ids].mean(dim=0).detach()


def similarity(a: str, b: str) -> float:
    return torch.nn.functional.cosine_similarity(token_vector(a), token_vector(b), dim=0).item()


def compare(anchor: str, others: list[str]) -> list[float]:
    print(f"\n{anchor!r}")
    scores = []
    for word in sorted(others, key=lambda w: similarity(anchor, w), reverse=True):
        n = len(tokenizer(word).input_ids)
        note = f"  ({n} tokens, averaged)" if n > 1 else ""
        print(f"  vs {word!r:<14} {similarity(anchor, word):.3f}{note}")
    return [similarity(anchor, w) for w in others]


title("3. Cosine similarity between token embeddings")
destinations = [" Madrid", " Porto", " Rome", " Tokyo", " pizza", " keyboard"]
dest_scores = compare(" Lisbon", destinations)
compare(" hotel", [" motel", " hostel", " airport", " resort", " banana", " algorithm"])
compare(" Bali", [" Thailand", " Hawaii", " Iceland", " Maldives", " Monday", " Excel"])
print("\nRelated words score higher than unrelated ones, without anyone writing that rule.")
print("Only the order matters: the absolute values depend on the model.")


# -----------------------------------------------------------------------------
# 4. Position is not in the vector
# -----------------------------------------------------------------------------
# The same token gets the same vector wherever it appears. The first Transformers
# added a position vector to it; Qwen2.5 uses rotary position embeddings (RoPE),
# applied inside attention instead.

title("4. Position is not in the vector")
found = []
for sentence in ["Fly to Lisbon from Madrid", "Fly to Madrid from Lisbon"]:
    sentence_ids = encode(tokenizer, sentence)
    p = sentence_ids[0].tolist().index(lisbon_id)
    with torch.no_grad():
        found.append(table(sentence_ids)[0, p])
    print(f"{sentence!r:<30} ' Lisbon' at position {p}")
print(f"Same input vector in both sentences: {torch.equal(found[0], found[1])}")
rotary = [name for name, _ in model.named_modules() if "rotary" in name]
print(f"Position module in this model: {rotary}")


# -----------------------------------------------------------------------------
# Chart
# -----------------------------------------------------------------------------

order = sorted(range(len(destinations)), key=lambda i: dest_scores[i], reverse=True)
fig, ax = plt.subplots(figsize=(8, 4))
colors = [ACCENT if destinations[i] not in (" pizza", " keyboard") else NEUTRAL for i in order]
ax.bar([repr(destinations[i]) for i in order], [dest_scores[i] for i in order], color=colors)
ax.set_title("Cosine similarity to ' Lisbon' (input embeddings)")
ax.set_ylabel("Cosine similarity")
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
show_or_save(fig, "2-embeddings")
