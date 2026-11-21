"""
1. The window of a small local model, and what fits in it
=========================================================

Qwen2.5-0.5B-Instruct runs on your computer (no API key; the first run
downloads about 1 GB). The script prints the model's context limit, then asks
two questions about contracts of growing size: find one fact, and count the
clauses with a penalty. Greedy decoding, so every run gives the same answers.

    uv run 1-local-limit.py
"""

import json
import time
from datetime import date

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from contract import HERE, QUESTIONS, build

model_id = "Qwen/Qwen2.5-0.5B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32)
print(f"{model_id}: context limit {model.config.max_position_embeddings:,} tokens ({date.today().isoformat()})\n")

rows = []
for n in [10, 40, 160, 480]:
    contract, expected = build(n)
    for kind, question in QUESTIONS.items():
        messages = [{"role": "user", "content": f"{contract}\n\n{question} Reply with the number only."}]
        ids = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt", return_dict=True).input_ids
        start = time.time()
        out = model.generate(ids, max_new_tokens=8, do_sample=False)  # greedy: same answer every run
        answer = tokenizer.decode(out[0, ids.shape[1]:], skip_special_tokens=True).strip()
        rows.append({"clauses": n, "tokens": ids.shape[1], "question": kind, "answer": answer,
                     "expected": expected[kind], "seconds": round(time.time() - start, 1)})
        r = rows[-1]
        print(f"{n:>4} clauses  {r['tokens']:>6,} tokens  {kind:<6}  answer {answer:>4}  expected {r['expected']:>4}  {r['seconds']:>5}s")

(HERE / "results" / "local-limit.json").write_text(json.dumps(
    {"model": model_id, "date": date.today().isoformat(), "limit": model.config.max_position_embeddings, "rows": rows}, indent=2))
