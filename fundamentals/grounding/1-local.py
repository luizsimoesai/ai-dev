"""
1. A small local model, three settings
======================================

Qwen2.5-0.5B-Instruct runs on your computer (no API key; the first run
downloads about 1 GB). Eight questions about a fictional dehumidifier, in
three settings: without the manual; with the manual and a rule ("if the manual
doesn't say, say so"); and with the manual, the rule and one example of each
behavior. Greedy decoding, so one run per setting gives the same answers every
time. Saves results/local.json.

    uv run 1-local.py
"""

import json
from collections import Counter
from datetime import date

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from manual import HERE, QUESTIONS, SETTINGS, label, messages, numbers_not_in_manual

model_id = "Qwen/Qwen2.5-0.5B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32)

rows = []
print(f"{model_id} ({date.today().isoformat()})")
for setting in SETTINGS:
    print(f"\n{setting}")
    for question, check in QUESTIONS:
        ids = tokenizer.apply_chat_template(messages(setting, question), add_generation_prompt=True,
                                            return_tensors="pt", return_dict=True).input_ids
        out = model.generate(ids, max_new_tokens=60, do_sample=False)  # greedy
        answer = tokenizer.decode(out[0, ids.shape[1]:], skip_special_tokens=True).strip().replace("\n", " ")
        rows.append({"setting": setting, "question": question, "label": label(check, answer, setting != "no manual"),
                     "numbers_not_in_manual": numbers_not_in_manual(answer), "answer": answer})
        r = rows[-1]
        flag = f"  [numbers not in manual: {', '.join(r['numbers_not_in_manual'])}]" if r["numbers_not_in_manual"] else ""
        print(f"  {question:<43} {r['label']:<21} {answer[:70]}{flag}")
    print("  " + ", ".join(f"{k}: {v}" for k, v in Counter(r["label"] for r in rows if r["setting"] == setting).items()))

(HERE / "results" / "local.json").write_text(
    json.dumps({"model": model_id, "date": date.today().isoformat(), "rows": rows}, indent=2))
