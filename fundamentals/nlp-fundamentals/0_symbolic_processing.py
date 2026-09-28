# uv add spacy
# download the model:
# uv pip install https://github.com/explosion/spacy-models/releases/download/pt_core_news_sm-3.7.0/pt_core_news_sm-3.7.0-py3-none-any.whl


import spacy

# Load the Portuguese model
nlp = spacy.load("pt_core_news_sm")

# Sentence to analyze
sentence = "O menino joga bola alegremente no parque."

# Process the sentence
doc = nlp(sentence)

# Show part-of-speech tags
print(f"Sentence: {sentence}\n")

for token in doc:
    print(f"{token.text:<15} -> {token.pos_}")
