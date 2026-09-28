# Simple implementation of morphological similarity between words

def morphological_similarity(word1, word2):
    # Simple method based on shared characters
    chars1 = set(word1)
    chars2 = set(word2)
    similarity = len(chars1.intersection(chars2)) / len(chars1.union(chars2))
    return similarity

examples = [("swim", "swimming"), ("drink", "drinker"), ("think", "thinker")]

for w1, w2 in examples:
    sim = morphological_similarity(w1, w2)
    print(f"'{w1}' vs '{w2}': {sim:.2f} similarity")
