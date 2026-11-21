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
| `1-chat-template-and-tokens.py` | The model's spec sheet (vocabulary, vector size, blocks, parameters); how the chat template flattens `system`/`user` messages into one text; how that text becomes token IDs; why codes like `A-10432` cost many tokens; the same sentence in English, Portuguese, Spanish and Japanese; a multi-turn support conversation; the default system message the template adds; and how markers typed by a user can open a fake turn. |
| `2-embeddings.py` | Why an ID is only a label (`' Lisbon'`, `' Madrid'` and `' Porto'` have IDs far apart); the embedding table (151,936 rows x 896 numbers, 28% of the parameters, shared with the output layer); cosine similarity between travel words: `' Lisbon'` lands closer to `' Madrid'` and `' Porto'` than to `' pizza'`, `' hotel'` closer to `' motel'` than to `' banana'`, and `' Maldives'`, split into 2 tokens and averaged, lands far from `' Bali'`; the same token gets the same input vector in any position, and this model adds position later with RoPE. Saves a bar chart. |
| `3-transformer-blocks.py` | The 24 blocks in action: the model's layout (14 attention heads, vectors of 896 numbers, a feed-forward network of 4,864); a "logit lens" that reads the model's guess after each block: noise early on, then `'berra'` and `' Canberra'` in blocks 22 and 23, just before the final choice; which input tokens the last position attended to; the causal mask, with two contract clauses that only differ after `' it'` and give the same `' it'` vector in every block; how different words *before* `' it'` pull its vectors apart; and why attention pairs grow with the square of the length. Saves two charts. |
| `4-logits-and-sampling.py` | Logits for all ~152k tokens; how temperature (0.3, 1.0, 1.5) concentrates or spreads probability; how top-k and top-p cut the candidates before the draw. Then two travel requests, a fixed answer (Lisbon's airport code) and a creative one (something to do on a rainy afternoon): how many candidates `top_k=50` and `top_p=0.9` keep at each temperature (top-k always 50; top-p from 1 to thousands), and four whole answers per setting. Saves two charts: the top 20 candidates for the lab question, and top-p on the creative request. |
| `5-generation-loop.py` | The autoregressive loop written by hand: draw a token, append it, run the model again, stop at `<|im_end|>`. Prints the probability of every token drawn. Then the same loop completes a Python function (`is_palindrome`) one token at a time, showing the top 3 candidates and the growing input at each step; shows that the model keeps writing if the program ignores the end token; and samples six completions (one per seed) and runs each one against five test cases: 4 of 6 pass. Saves a chart. |
| `6-training-and-inference.py` | A customer-support assistant. A store policy in the context changes the answer, but a hash of every weight shows nothing changed. Six SGD steps on one example change the weights: the loss falls from 0.780 to 0.004, the model now says 45 days for returns, and also says shipping takes "45 business days" (a side effect). Then times prefill vs decode with and without the KV cache. `--with-base` also compares the base model `Qwen/Qwen2.5-0.5B` (one extra ~1 GB download). The training section peaks at about 6 GB of memory. |
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
uv run 6-training-and-inference.py              # add --with-base to compare with the base model
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
