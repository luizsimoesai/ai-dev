# LLM text path

Follow one question through a real Transformer, from the chat messages to the generated answer:

```
MESSAGES ─► CHAT TEMPLATE ─► TOKENS ─► EMBEDDINGS ─► TRANSFORMER BLOCKS ─► LOGITS ─► SAMPLING ─► next token
                                                                                                    │
                       ◄──────────────── appended to the input, repeat until the end token ◄────────┘
```

The model is [`Qwen/Qwen2.5-0.5B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) (about 494M parameters, 24 blocks). It runs locally on CPU or Apple Silicon: **no API key needed**. The first run downloads about 1 GB to `~/.cache/huggingface`.

## Files

| File | What it shows |
|---|---|
| `1-chat-template-and-tokens.py` | The model's spec sheet (vocabulary, vector size, blocks, parameters); how the chat template flattens `system`/`user` messages into one text; how that text becomes token IDs; why codes like `SKU-7XQ9-2B` cost many tokens. |
| `2-embeddings.py` | The embedding table (one vector per token) and cosine similarity: `' Paris'` lands closer to other cities than to `' banana'` or `' guitar'`. Saves a bar chart. |
| `3-transformer-blocks.py` | The 24 blocks in action. A "logit lens" reads the model's guess after each block: noise early on, then `'berra'` and `' Canberra'` in blocks 22 and 23, just before the final choice. Also shows which input tokens the last position attended to. Saves two charts. |
| `4-logits-and-sampling.py` | Logits for all ~152k tokens; how temperature (0.3, 1.0, 1.5) concentrates or spreads probability; how top-k and top-p cut the candidates before the draw. Saves a chart of the top 20 candidates. |
| `5-generation-loop.py` | The autoregressive loop written by hand: draw a token, append it, run the model again, stop at `<|im_end|>`. Prints the probability of every token drawn. Saves a chart. |
| `utils/common.py` | Shared settings (model, question, temperature, top-k, top-p, seed) and helpers. **Edit the settings here**; every script picks them up. |

Each script loads the model on its own, so they can run in any order; the numbering follows the path of the text.

## How to run

With [uv](https://docs.astral.sh/uv/), from this folder:

```bash
cd fundamentals/llm-text-path/
uv init --bare                 # once per folder
uv add -r requirements.txt     # creates .venv/ and uv.lock
uv run 1-chat-template-and-tokens.py
uv run 2-embeddings.py
uv run 3-transformer-blocks.py
uv run 4-logits-and-sampling.py
uv run 5-generation-loop.py
```

Charts are saved to `output/` (ignored by Git) and also open in a window when a display is available. To only save them, prefix the command with `MPLBACKEND=Agg`.

Without uv: `pip install -r requirements.txt` in a virtual environment, then `python <file>.py`.

## Try this

- **Watch a wrong answer form.** In `utils/common.py`, set `TEMPERATURE = 1.2`, `TOP_K = 0`, `TOP_P = 1.0`, `SEED = 5` and run `5-generation-loop.py`. The first draw picks `'Sy'` (13% chance) instead of `'The'`; after that, every token is likely, and the model confidently finishes "Sydney is the capital of Australia." High probability for each step does not make the sentence true.
- **Compare temperatures.** Change `TEMPERATURE` and rerun `4-logits-and-sampling.py`: the order of the candidates never changes, only how the probability is spread.
- **Change the question.** Edit `QUESTION`. Questions with less common facts show more doubt in the logit lens and in the generation loop.
- **Another model.** `utils/common.py` has a commented line for `Polygl0t/Tucano2-qwen-0.5B-Instruct` (28 blocks, tuned for Portuguese). Swap the `MODEL_ID` lines and write `SYSTEM` and `QUESTION` in Portuguese.

## Notes

- The loop in `5-generation-loop.py` reprocesses the whole sequence at every step, for clarity. `model.generate()` uses a KV cache to skip that repeated work.
- The model is loaded in float32, so NumPy can read the tensors and the numbers match from one machine to another.
- Outputs were checked with `torch 2.15`, `transformers 5.23`, `numpy 2.5` and `matplotlib 3.11` on Python 3.12.
