"""Generate the synthetic bank statements used in this folder (CSV).

Deterministic: the same seed always produces the same files.
    uv run make_statement.py   ->  statement-3m.csv  (2026-08-01 to 2026-10-31)
                                   statement-12m.csv (2025-11-01 to 2026-10-31)
All names, amounts and dates are made up.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
END = date(2026, 10, 31)
FILES = {"statement-3m.csv": date(2026, 8, 1), "statement-12m.csv": date(2025, 11, 1)}
HERE = Path(__file__).parent

# (description, category, min, max, average visits per week)
VARIABLE = [
    ("FRESHMART #212", "groceries", 18, 140, 1.6),
    ("GREENLEAF ORGANIC MARKET", "groceries", 12, 75, 0.6),
    ("CORNER BAKERY CO", "groceries", 4, 16, 1.0),
    ("LUIGI'S TRATTORIA", "restaurants", 28, 95, 0.4),
    ("SUSHI KOBO", "restaurants", 22, 80, 0.3),
    ("BEAN THERE COFFEE", "restaurants", 3.5, 9, 2.2),
    ("TACO RAPIDO", "restaurants", 9, 24, 0.6),
    ("METRO TRANSIT", "transport", 2.75, 2.75, 3.0),
    ("RIDEGO TRIP", "transport", 8, 38, 0.7),
    ("SHELL STATION 4471", "transport", 35, 68, 0.35),
    ("CITYPHARMA", "health", 6, 55, 0.4),
    ("BOOKNOOK", "shopping", 11, 48, 0.25),
    ("NORTHSTAR OUTFITTERS", "shopping", 25, 210, 0.3),
    ("SHOPZONE ONLINE", "shopping", 9, 160, 0.6),
    ("CINEPLEX 9", "entertainment", 12, 34, 0.3),
]

# (description, category, amount, day of month); negative = money out
FIXED = [
    ("ACME CORP PAYROLL", "income", 3250.00, 5),
    ("ACME CORP PAYROLL", "income", 3250.00, 20),
    ("MAPLE RESIDENCES RENT", "rent", -1450.00, 1),
    ("CITY POWER & LIGHT", "utilities", None, 12),
    ("AQUA CITY WATER", "utilities", None, 15),
    ("FIBERLINK INTERNET", "utilities", -59.90, 18),
    ("STREAMFLIX", "subscriptions", -15.49, 7),
    ("TUNEWAVE MUSIC", "subscriptions", -10.99, 11),
    ("CLOUDBOX STORAGE", "subscriptions", -2.99, 23),
    ("IRONWORKS GYM", "health", -42.00, 3),
    ("TRANSFER TO SAVINGS", "transfers", -400.00, 21),
]


def money(x: float) -> float:
    return round(x, 2)


def rows(start: date, rng: random.Random):
    out = []
    month = start
    while month <= END:
        for desc, cat, amount, day in FIXED:
            d = month.replace(day=day)
            if amount is None:  # variable utility bills
                amount = -money(rng.uniform(70, 140) if "POWER" in desc else rng.uniform(28, 55))
            out.append((d, desc, cat, money(amount)))
        month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)

    d = start
    while d <= END:
        for desc, cat, lo, hi, per_week in VARIABLE:
            if rng.random() < per_week / 7:
                out.append((d, desc, cat, -money(rng.uniform(lo, hi))))
        d += timedelta(days=1)

    # A few one-off events that make questions less trivial
    out += [
        (date(2026, 8, 14), "SHOPZONE ONLINE REFUND", "shopping", 64.90),
        (date(2026, 9, 9), "DR. PATEL DENTAL", "health", -230.00),
        (date(2026, 9, 26), "VENMO FROM J. RIVERA", "transfers", 85.00),
        (date(2026, 10, 3), "SKYWAY AIRLINES", "transport", -386.40),
        (date(2026, 10, 17), "HOMEBASE HARDWARE", "shopping", -127.35),
        (date(2026, 10, 29), "LUIGI'S TRATTORIA", "restaurants", -142.80),
    ]
    out.sort(key=lambda r: (r[0], r[1]))
    return out


def main() -> None:
    for name, start in FILES.items():
        data = rows(start, random.Random(SEED))  # a fresh generator per file, same seed
        with (HERE / name).open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "description", "category", "amount"])
            for d, desc, cat, amt in data:
                w.writerow([d.isoformat(), desc, cat, f"{amt:.2f}"])
        print(f"{len(data)} transactions -> {name}")


if __name__ == "__main__":
    main()
