"""Shared pieces: a short product manual, eight questions and the grading.

The product is fictional (the "Brisa D-300" dehumidifier), so no model can know
it from training: anything it says that is not in the manual was made up.
Five questions are answered by the manual; three are not.

Each answer gets one label, checked in code against the manual:
With the manual in the prompt:
- grounded:            a covered question, answered as the manual says;
- not as the manual:   a covered question, answered differently (wrong or opposite);
- false absence:       a covered question, but the answer says the manual doesn't cover it;
- acknowledged absence: an uncovered question, and the answer says so;
- invented:            an uncovered question, answered anyway.
Without the manual: "says it doesn't know", "matches manual, no source" (a
lucky match), "not as the manual" or "invented".
"""

import re
from pathlib import Path

HERE = Path(__file__).parent

MANUAL = """Brisa D-300 Dehumidifier: User Manual (excerpt)

1. Specifications. Water tank capacity: 3 liters. Recommended room size: up to 30 square meters. Power supply: 220-240 V, 50 Hz. Weight: 11 kg.
2. Operation. Press POWER to start. The default target humidity is 50%. Use the arrow buttons to set it between 35% and 70%, in steps of 5%.
3. Full tank. When the tank is full, the unit stops and the TANK light turns orange. Empty the tank and put it back to restart.
4. Maintenance. Clean the air filter every 2 weeks with lukewarm water. Do not use detergents. Let the filter dry before putting it back.
5. Error codes. E1: humidity sensor fault, contact support. E4: air filter blocked, clean the filter. E7: room temperature below 5 degrees C, the unit pauses.
6. Warranty. The Brisa D-300 has a 24-month warranty from the date of purchase. The warranty does not cover damage caused by using detergents on the filter.
"""

ABSTAIN = "The manual does not cover this."

# (question, check for a covered question, or None when the manual doesn't cover it)
QUESTIONS = [
    ("How long is the warranty?", r"\b24\b|two[ -]years?|2[ -]years?"),
    ("What does error code E4 mean?", r"filter"),
    ("How often should I clean the air filter?", r"2 weeks|two weeks|every 2\b|biweekly"),
    ("What is the default target humidity?", r"\b50\s?%"),
    ("Can I use detergent to clean the filter?", r"\b(no|not|don't|cannot|can't|shouldn't)\b"),
    ("What is the noise level in decibels?", None),
    ("Does it connect to a phone app over Wi-Fi?", None),
    ("What does error code E9 mean?", None),
]

SAYS_NOT_COVERED = re.compile(  # the answer says the manual (or the model) has no information on it
    r"\bmanual\b[^.]{0,40}?\b(does not|doesn't|did not)\s+(cover|mention|say|specify|state|include|list|provide|address)\b"
    r"|\bnot (explicitly )?(covered|mentioned|stated|specified|listed|included) (in|by) the manual\b"
    r"|don't have (reliable |specific |the )?[\w'’ -]{0,40}?(information|details|specifications|manual)\b"
    r"|\bno (specific )?information\b|not familiar with|not aware of|can't confirm|cannot confirm", re.I)

SYSTEM_RULE = f"Answer only from the manual below. If the manual does not say, reply exactly: {ABSTAIN}\n\n{MANUAL}"
EXAMPLE = [  # one example of each behavior, for the third setting
    {"role": "user", "content": "What colour is the unit? Answer in one sentence."},
    {"role": "assistant", "content": ABSTAIN},
    {"role": "user", "content": "What is the weight? Answer in one sentence."},
    {"role": "assistant", "content": "The Brisa D-300 weighs 11 kg."},
]


def messages(setting: str, question: str) -> list[dict]:
    """The three settings: no manual; manual + rule; manual + rule + one example of each behavior."""
    q = f"{question} Answer in one sentence."
    if setting == "no manual":
        return [{"role": "user", "content": f"About the Brisa D-300 dehumidifier: {q}"}]
    if setting == "manual + rule":
        return [{"role": "system", "content": SYSTEM_RULE}, {"role": "user", "content": q}]
    return [{"role": "system", "content": SYSTEM_RULE}, *EXAMPLE, {"role": "user", "content": q}]


SETTINGS = ["no manual", "manual + rule", "manual + rule + example"]


def label(check: str | None, answer: str, has_source: bool = True) -> str:
    """Grade one answer against the manual. Without the manual in the prompt, a
    covered question answered like the manual is a lucky match, not grounding."""
    not_covered = bool(SAYS_NOT_COVERED.search(answer))
    if not has_source:
        if not_covered:
            return "says it doesn't know"
        if check is None:
            return "invented"
        ok = re.search(check, answer, re.I) and not re.match(r"\s*yes\b", answer, re.I)
        return "matches manual, no source" if ok else "not as the manual"
    if check is None:
        return "acknowledged absence" if not_covered else "invented"
    if not_covered:
        return "false absence"
    if re.match(r"\s*yes\b", answer, re.I) or not re.search(check, answer, re.I):
        return "not as the manual"
    return "grounded"


def numbers_not_in_manual(answer: str) -> list[str]:
    """A narrow check in code: every number in the answer must appear in the manual."""
    return sorted(set(re.findall(r"\d+", answer)) - set(re.findall(r"\d+", MANUAL)))
