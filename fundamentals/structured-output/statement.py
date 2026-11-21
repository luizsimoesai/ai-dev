"""Shared pieces: synthetic statements, the schema, the prompt and the checks.

statement.csv is synthetic (made-up merchants and amounts, in US dollars).
Ten short excerpts of 3 to 6 rows are rendered as plain text, the way a bank
statement looks when copied from a PDF. The task: extract every transaction
as JSON with a date, a description, an amount and one category from a fixed list.
"""

import csv
import json
import random
import re
from pathlib import Path

HERE = Path(__file__).parent
ROWS = list(csv.DictReader(open(HERE / "statement.csv")))
CATEGORIES = sorted({r["category"] for r in ROWS})
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

_rng = random.Random(3)
SAMPLES = []  # ten excerpts, each a list of consecutive CSV rows
for _ in range(10):
    k = _rng.randint(3, 6)
    start = _rng.randrange(0, len(ROWS) - k)
    SAMPLES.append(ROWS[start:start + k])


def render(rows: list[dict]) -> str:
    """A statement excerpt as plain text."""
    lines = [f"ACCOUNT STATEMENT  {rows[0]['date']} to {rows[-1]['date']}"]
    for r in rows:
        _, m, d = r["date"].split("-")
        a = float(r["amount"])
        amount = f"{'+' if a > 0 else '-'}{abs(a):,.2f}"
        lines.append(f"{MONTHS[int(m) - 1]} {d}   {r['description']:<28}{amount:>12}")
    return "\n".join(lines)


INSTRUCTIONS = ("Extract every transaction from the bank statement below. Use ISO dates (YYYY-MM-DD), "
                "negative amounts for money out, and one category from: " + ", ".join(CATEGORIES) + ".\n"
                'Reply with JSON only, in this shape: {"transactions": [{"date": "...", "description": "...", '
                '"amount": 0.0, "category": "..."}]}')


def prompt(rows: list[dict]) -> str:
    return f"{INSTRUCTIONS}\n\n{render(rows)}"


SCHEMA = {  # JSON Schema of the answer
    "type": "object",
    "properties": {"transactions": {"type": "array", "items": {
        "type": "object",
        "properties": {"date": {"type": "string", "description": "YYYY-MM-DD"},
                       "description": {"type": "string"},
                       "amount": {"type": "number", "description": "negative for money out"},
                       "category": {"type": "string", "enum": CATEGORIES}},
        "required": ["date", "description", "amount", "category"],
        "additionalProperties": False}}},
    "required": ["transactions"],
    "additionalProperties": False,
}


def validate(text: str) -> tuple[str, list | None]:
    """Format: 'not JSON', 'breaks schema' or 'valid' (with the transactions)."""
    try:
        data = json.loads(text)
    except ValueError:
        return "not JSON", None
    try:
        tx = data["transactions"]
        assert isinstance(tx, list)
        for t in tx:
            assert set(t) == {"date", "description", "amount", "category"}
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", t["date"])
            assert isinstance(t["amount"], (int, float)) and t["category"] in CATEGORIES
    except (AssertionError, KeyError, TypeError):
        return "breaks schema", None
    return "valid", tx


def code_check(rows: list[dict], tx: list) -> list[str]:
    """Checks that need no model and no answer key, only the statement text:
    one transaction per dated line, and every amount (with its sign) in the text."""
    text = render(rows)
    problems = []
    dated_lines = len(re.findall(r"^[A-Z][a-z]{2} \d{2} ", text, re.M))
    if len(tx) != dated_lines:
        problems.append(f"{len(tx)} transactions for {dated_lines} dated lines")
    in_text = {float(a.replace(",", "")) for a in re.findall(r"[+-][\d,]+\.\d{2}", text)}
    missing = [t["amount"] for t in tx if round(t["amount"], 2) not in in_text]
    if missing:
        problems.append(f"amounts not in the statement: {missing}")
    return problems


def score(rows: list[dict], tx: list) -> dict:
    """Compare with the answer key (the CSV), row by row."""
    pairs = list(zip(tx, rows))
    return {"rows": len(tx) == len(rows),
            "date": sum(t["date"] == r["date"] for t, r in pairs),
            "amount": sum(abs(t["amount"] - float(r["amount"])) < 0.005 for t, r in pairs),
            "category": sum(t["category"] == r["category"] for t, r in pairs)}


def summary(results: list[dict]) -> list[str]:
    """results: one dict per sample with 'rows' (the CSV rows) and 'text' (the model's answer)."""
    fmt = {"valid": 0, "breaks schema": 0, "not JSON": 0}
    acc = {"date": 0, "amount": 0, "category": 0}
    rows_in_valid = wrong = caught = right = false_alarm = 0
    for r in results:
        f, tx = validate(r["text"])
        fmt[f] += 1
        if tx is None:
            continue
        rows_in_valid += len(r["rows"])
        s = score(r["rows"], tx)
        for k in acc:
            acc[k] += s[k]
        flagged = bool(code_check(r["rows"], tx))
        if not s["rows"] or s["date"] < len(r["rows"]) or s["amount"] < len(r["rows"]):
            wrong += 1
            caught += flagged
        else:
            right += 1
            false_alarm += flagged
    return [f"format: valid {fmt['valid']}/10, breaks schema {fmt['breaks schema']}, not JSON {fmt['not JSON']}",
            f"valid answers: right out of their {rows_in_valid} rows: " + ", ".join(f"{k} {v}" for k, v in acc.items()),
            f"code check: caught {caught} of {wrong} valid answers with a wrong row count, date or amount; "
            f"flagged {false_alarm} of {right} right ones"]
