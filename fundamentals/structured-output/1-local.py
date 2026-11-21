"""
1. Asking for JSON vs constraining the generation (local model)
===============================================================

Qwen2.5-0.5B-Instruct extracts the transactions of ten statement excerpts,
two ways, greedy (one run gives the same answer every time):

- prompt only: the prompt asks for JSON in a given shape;
- constrained: the code writes the fixed parts of the JSON itself (braces,
  quotes, key names) and calls the model only inside the fields, keeping just
  the tokens that fit the field (a date, a number, a category from the list).

This is a minimal constrained decoder, written to show the idea: it recomputes
the whole sequence at every step, so it is slow. Libraries such as SGLang,
Outlines or llguidance do the same thing fast. No API key; the first run
downloads about 1 GB. Saves results/local.json.

    uv run --with-requirements requirements.txt 1-local.py
"""

import json
from datetime import date

import regex
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from statement import CATEGORIES, HERE, SAMPLES, prompt, summary

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32)
VOCAB = [tok.decode([i]) for i in range(len(tok))]  # the text of every token
SPECIAL = set(tok.all_special_ids)


def chat_ids(text):
    return tok.apply_chat_template([{"role": "user", "content": text}], add_generation_prompt=True,
                                   return_tensors="pt", return_dict=True).input_ids[0].tolist()


class Constrained:
    def __init__(self, ids):
        self.ids, self.text, self.model_calls, self.forced = list(ids), "", 0, 0

    def force(self, literal):  # fixed text: written by the code, no model call
        new = tok.encode(literal, add_special_tokens=False)
        self.ids += new
        self.text += literal
        self.forced += len(new)

    def step(self, allowed):  # one model call; keep the most likely token that is allowed
        self.model_calls += 1
        with torch.no_grad():
            logits = model(torch.tensor([self.ids])).logits[0, -1]
        for i in torch.argsort(logits, descending=True)[:5000].tolist():
            if i not in SPECIAL and VOCAB[i] and allowed(VOCAB[i]):
                self.ids.append(i)
                self.text += VOCAB[i]
                return VOCAB[i]
        raise RuntimeError("no allowed token")

    def field(self, pattern, then):
        """Generate one field: every token must keep `field + then` a possible match."""
        cur = ""
        while True:
            cur += self.step(lambda t: regex.fullmatch(pattern + regex.escape(then), cur + t, partial=True) is not None)
            m = regex.match(pattern, cur)
            if m and cur[m.end():] and then.startswith(cur[m.end():]):
                self.force(then[len(cur) - m.end():])  # the rest of the fixed text
                return

    def last_field(self, pattern):
        """The category, then the model's choice: '"},' (another transaction) or '"}]' (the end)."""
        cur, end = "", r'"\s*\}\s*(?P<next>,|\])\s*\}?'
        while True:
            cur += self.step(lambda t: regex.fullmatch(pattern + end, cur + t, partial=True) is not None)
            m = regex.match(pattern + r'"\s*\}\s*(?P<next>,|\])', cur)
            if m:
                if m.group("next") == ",":
                    self.force(" {")
                    return "more"
                if not cur.rstrip().endswith("}"):
                    self.force("}")
                return "end"


def constrained(text):
    g = Constrained(chat_ids(text))
    g.force('{"transactions": [{"date": "')
    for _ in range(20):
        g.field(r"\d{4}-\d{2}-\d{2}", '", "description": "')
        g.field(r'[^"\\\n]{1,60}', '", "amount":')  # the space before the number is left to the model
        g.field(r" ?-?\d{1,7}(\.\d{1,2})?", ', "category": "')
        if g.last_field("(" + "|".join(CATEGORIES) + ")") == "end":
            break
        g.force('"date": "')
    return g.text, g.model_calls, g.forced


out = {"model": MODEL, "date": date.today().isoformat(), "prompt only": [], "constrained": []}
for rows in SAMPLES:
    ids = torch.tensor([chat_ids(prompt(rows))])
    gen = model.generate(ids, max_new_tokens=500, do_sample=False)
    out["prompt only"].append({"rows": rows, "text": tok.decode(gen[0, ids.shape[1]:], skip_special_tokens=True).strip()})
    text, calls, forced = constrained(prompt(rows))
    out["constrained"].append({"rows": rows, "text": text, "model_calls": calls, "forced_tokens": forced})

print(f"{MODEL} ({out['date']}), {len(SAMPLES)} statement excerpts, {sum(map(len, SAMPLES))} rows")
for name in ["prompt only", "constrained"]:
    print(f"\n{name}")
    for line in summary(out[name]):
        print("  " + line)
calls = sum(r["model_calls"] for r in out["constrained"])
forced = sum(r["forced_tokens"] for r in out["constrained"])
print(f"  tokens written by the code, no model call: {forced} of {calls + forced} ({forced / (calls + forced):.0%})")
(HERE / "results" / "local.json").write_text(json.dumps(out, indent=2))
