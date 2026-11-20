"""
1. Chat template and tokens: from messages to the numbers the model reads
==========================================================================

    MESSAGES ──► CHAT TEMPLATE ──► TOKENS ──► IDs
    (roles)      (one long text)   (pieces)   (integers)

Run from this folder:
    uv run 1-chat-template-and-tokens.py

Edit QUESTION and SYSTEM in utils/common.py to try other prompts.
"""

from utils.common import MODEL_ID, QUESTION, SYSTEM, build_prompt, encode, load_model, title

# -----------------------------------------------------------------------------
# 0. Load the model
# -----------------------------------------------------------------------------
# An LLM comes in two pieces, both downloaded from Hugging Face on first run:
#   - the TOKENIZER: fixed rules that turn text into numbers and back;
#   - the MODEL: the neural network, i.e. millions of weights learned in training.

title(f"0. Load {MODEL_ID}")
tokenizer, model = load_model()

# model.config is the model's spec sheet (the config.json downloaded with the weights).
#   vocab_size:        how many different tokens the model knows
#   hidden_size:       how many numbers describe each token (vector size)
#   num_hidden_layers: how many stacked blocks the text goes through
cfg = model.config
print(f"Vocabulary: {cfg.vocab_size:,} tokens | vectors of {cfg.hidden_size} numbers | "
      f"{cfg.num_hidden_layers} Transformer blocks")
# Shared matrices (here the embedding table, reused by the output layer) count once.
print(f"Parameters: {sum(p.numel() for p in model.parameters()) / 1e6:.0f} million")


# -----------------------------------------------------------------------------
# 1. Messages with roles
# -----------------------------------------------------------------------------
# In a chat, the input is a list of messages, each with a role.
# The network, though, only reads ONE continuous text.

title("1. Messages with roles (system / user)")
for role, content in [("system", SYSTEM), ("user", QUESTION)]:
    print(f"[{role}] {content}")


# -----------------------------------------------------------------------------
# 2. Chat template
# -----------------------------------------------------------------------------
# The chat template flattens the conversation into that single text, adding
# special markers the model learned to read as turn changes.

title("2. Chat template: the single text the model actually reads")
text = build_prompt(tokenizer)
print(text)
print("<|im_start|> and <|im_end|> mark who is speaking. The last line opens the")
print("assistant's turn: the model simply CONTINUES this text.")


# -----------------------------------------------------------------------------
# 3. Tokenization
# -----------------------------------------------------------------------------
# The tokenizer splits the text into pieces from its vocabulary (whole words,
# parts of words, symbols) and replaces each piece with its ID. From here on,
# the network only handles numbers.

title("3. Tokenization: text -> pieces -> IDs")
ids = encode(tokenizer, text)
for pos, token_id in enumerate(ids[0].tolist()):
    print(f"{pos:>3}  ID {token_id:>6}  {tokenizer.decode([token_id])!r}")
print(f"\n{len(text)} characters became {ids.shape[1]} tokens.")

# max_position_embeddings is the context window: the most tokens (input + answer)
# the model can process at once.
window = cfg.max_position_embeddings
print(f"Context window: {ids.shape[1]} of {window:,} possible tokens "
      f"({100 * ids.shape[1] / window:.2f}%), not counting the answer.")


# -----------------------------------------------------------------------------
# 4. Common words vs. rare strings
# -----------------------------------------------------------------------------
# Frequent words are usually one token; codes and rare words split into many.

title("4. Common words vs. rare strings")
for sample in ["capital", " capital", "Canberra", "SKU-7XQ9-2B", "unconstitutionally"]:
    pieces = [tokenizer.decode([t]) for t in tokenizer(sample).input_ids]
    unit = "token " if len(pieces) == 1 else "tokens"
    print(f"{sample!r:<24} {len(pieces):>2} {unit}  {pieces}")
print("A leading space is part of the token: 'capital' and ' capital' differ.")


# -----------------------------------------------------------------------------
# 5. Back to text
# -----------------------------------------------------------------------------
# Decoding is the reverse trip: IDs -> pieces -> joined text.

title("5. Decoding: IDs -> text")
round_trip = tokenizer.decode(ids[0])
print("Same text after encoding and decoding:", round_trip == text)
