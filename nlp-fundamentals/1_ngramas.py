from collections import Counter, defaultdict

# Corpus simples em português
corpus = [
    "o gato dorme no sofá",
    "o gato come ração",
    "o cachorro dorme no chão",
    "o cachorro come carne",
    "a menina brinca no parque",
    "a menina come frutas",
    "o menino joga bola",
    "o menino corre rápido",
    "o sol brilha forte",
    "a lua brilha à noite",
    "o pássaro voa alto",
    "o pássaro canta bem"
]

# Construir modelo de bigramas
bigramas = defaultdict(Counter)

for frase in corpus:
    palavras = frase.split()
    for i in range(len(palavras) - 1):
        palavra_atual = palavras[i]
        proxima = palavras[i + 1]
        bigramas[palavra_atual][proxima] += 1

# Função para mostrar probabilidades
def prever_proxima(palavra):
    if palavra not in bigramas:
        print(f"Palavra '{palavra}' não encontrada")
        return
    
    total = sum(bigramas[palavra].values())
    print(f"\nApós '{palavra}':")
    
    for prox, freq in bigramas[palavra].most_common():
        prob = freq / total
        print(f"  '{prox}': {prob:.1%} ({freq}/{total})")

# Testar o modelo
prever_proxima("o")
prever_proxima("gato")
prever_proxima("come")
prever_proxima("no")