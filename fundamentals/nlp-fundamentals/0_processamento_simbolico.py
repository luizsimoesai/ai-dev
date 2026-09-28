# uv add spacy
# baixar o modelo: 
# uv pip install https://github.com/explosion/spacy-models/releases/download/pt_core_news_sm-3.7.0/pt_core_news_sm-3.7.0-py3-none-any.whl


import spacy

# Carregar o modelo em português
nlp = spacy.load("pt_core_news_sm")

# Frase para análise
frase = "O menino joga bola alegremente no parque."

# Processar a frase
doc = nlp(frase)

# Mostrar classificação gramatical
print(f"Frase: {frase}\n")

for token in doc:
    print(f"{token.text:<15} -> {token.pos_}")