"""
1. A vague vs a structured system prompt (local model)
======================================================

Qwen2.5-0.5B-Instruct answers the eight customer messages of cases.py with
each system prompt, greedy (one run gives the same answers every time). No API
key; the first run downloads about 1 GB. Saves results/local.json.

    uv run --with-requirements requirements.txt 1-local.py
"""

import json
from datetime import date

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from cases import CASES, HERE, PROMPTS, messages, report

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32)

rows = []
for prompt in PROMPTS:
    for case in CASES:
        ids = tokenizer.apply_chat_template(messages(prompt, case), add_generation_prompt=True,
                                            return_tensors="pt", return_dict=True).input_ids
        out = model.generate(ids, max_new_tokens=120, do_sample=False)
        answer = tokenizer.decode(out[0, ids.shape[1]:], skip_special_tokens=True).strip().replace("\n", " ")
        rows.append({"prompt": prompt, "case": case, "answer": answer})

print(f"{MODEL} ({date.today().isoformat()})\n")
print("\n".join(report(rows)))
(HERE / "results" / "local.json").write_text(json.dumps({"model": MODEL, "date": date.today().isoformat(), "rows": rows}, indent=2))
