"""Shared helpers for the llm-text-path scripts.

Every numbered script loads the same small model and builds the same prompt,
so the outputs line up from one file to the next.
"""

from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# -----------------------------------------------------------------------------
# Configuration (edit here; every script picks it up)
# -----------------------------------------------------------------------------

# Qwen2.5 (Sep 2024): multilingual Transformer, ~494M parameters, 24 blocks.
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
# Alternative for Portuguese prompts (Tucano2, Feb 2026, 28 blocks, tuned for
# Portuguese by Polygl0t). Swap the lines and translate SYSTEM and QUESTION.
# MODEL_ID = "Polygl0t/Tucano2-qwen-0.5B-Instruct"

SYSTEM = "You are a helpful assistant. Answer in one short sentence."
QUESTION = "What is the capital of Australia?"

TEMPERATURE = 0.7  # > 0. Lower = more predictable; higher = more varied.
TOP_K = 50  # keep only the K most likely candidates. 0 = off.
TOP_P = 0.9  # keep the most likely candidates until their sum reaches P. 1.0 = off.
MAX_NEW_TOKENS = 20  # length limit for the answer
SEED = 7  # same seed = same random draws

# Chart colors: one accent for the data, a neutral for anything secondary.
ACCENT = "#4698D5"
NEUTRAL = "#94A3B8"
INK = "#475569"

# Charts are saved here (and also shown on screen when a display is available).
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def title(text: str) -> None:
    print(f"\n{'=' * 70}\n{text}\n{'=' * 70}")


def load_model(eager_attention: bool = False):
    """Load the tokenizer and the model (downloaded to ~/.cache/huggingface once).

    eager_attention=True computes attention explicitly, so the attention
    weights can be read back (used in 3-transformer-blocks.py).
    """
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    kwargs = {"attn_implementation": "eager"} if eager_attention else {}
    # float32 so NumPy can read the tensors and the numbers match on every machine
    # (recent transformers versions load this model in bfloat16 by default).
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32, **kwargs)
    model.eval()  # inference mode, not training
    return tokenizer, model


def build_prompt(tokenizer) -> str:
    """Messages with roles -> the single text the model actually reads."""
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": QUESTION},
    ]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def encode(tokenizer, text: str) -> torch.Tensor:
    return tokenizer(text, return_tensors="pt").input_ids  # shape (1, n_tokens)


def probabilities(logits: torch.Tensor, temperature: float) -> np.ndarray:
    """Logits / temperature, then softmax: turns scores into probabilities."""
    return torch.softmax(logits.double() / temperature, dim=-1).numpy()


def top_filter(prob: np.ndarray, top_k: int, top_p: float) -> np.ndarray:
    """Apply top-k, then top-p: zero out the cut candidates and renormalize.

    - top-k keeps only the K most likely candidates.
    - top-p ("nucleus") walks from the most to the least likely candidate,
      adding up probabilities, and stops once the sum reaches P. How many
      survive depends on the model's confidence.
    """
    order = np.argsort(prob)[::-1]
    p = prob[order].copy()
    if top_k > 0:
        p[top_k:] = 0
        p = p / p.sum()
    if top_p < 1.0:
        sum_before = np.cumsum(p) - p  # probability already added before each candidate
        p[sum_before >= top_p] = 0  # keeps the candidate that crosses the threshold
        p = p / p.sum()
    filtered = np.zeros_like(prob)
    filtered[order] = p
    return filtered


def show_or_save(fig, name: str) -> None:
    """Save the chart to output/ and show it when a display is available."""
    import matplotlib
    import matplotlib.pyplot as plt

    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"{name}.png"
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    print(f"\nChart saved to {path}")
    if matplotlib.get_backend().lower() != "agg":
        print("Close the chart window to finish.")
        plt.show()
