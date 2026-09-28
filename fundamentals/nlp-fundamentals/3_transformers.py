# $ uv add transformers
# $ uv add torch

from transformers import pipeline

# Use a valid model (Portuguese BERT mask)
fill_mask = pipeline("fill-mask", model="neuralmind/bert-base-portuguese-cased")

results = fill_mask("O gato pulou no muro, agora ele está em cima do [MASK] alpendre.")
for r in results:
    print(r['sequence'], "~", round(r['score'], 2))
