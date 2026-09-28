# Simples implementação de similaridade morfológica entre palavras

def similaridade_morfological(palavra1, palavra2):
    # Método simples baseado em caracteres compartilhados
    chars1 = set(palavra1)
    chars2 = set(palavra2)
    similaridade = len(chars1.intersection(chars2)) / len(chars1.union(chars2))
    return similaridade

exemplos = [("nadar", "nadando"), ("beber", "bebedor"), ("pensar", "pensador")]

for p1, p2 in exemplos:
    sim = similaridade_morfological(p1, p2)
    print(f"'{p1}' vs '{p2}': {sim:.2f} de similaridade")