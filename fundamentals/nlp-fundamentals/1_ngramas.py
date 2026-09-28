from collections import Counter, defaultdict

# Simple English corpus
corpus = [
    "the cat sleeps on the couch",
    "the cat eats food",
    "the dog sleeps on the floor",
    "the dog eats meat",
    "the girl plays in the park",
    "the girl eats fruit",
    "the boy plays ball",
    "the boy runs fast",
    "the sun shines bright",
    "the moon shines at night",
    "the bird flies high",
    "the bird sings well"
]

# Build bigram model
bigrams = defaultdict(Counter)

for sentence in corpus:
    words = sentence.split()
    for i in range(len(words) - 1):
        current_word = words[i]
        next_word = words[i + 1]
        bigrams[current_word][next_word] += 1

# Function to show probabilities
def predict_next(word):
    if word not in bigrams:
        print(f"Word '{word}' not found")
        return

    total = sum(bigrams[word].values())
    print(f"\nAfter '{word}':")

    for next_word, freq in bigrams[word].most_common():
        prob = freq / total
        print(f"  '{next_word}': {prob:.1%} ({freq}/{total})")

# Test the model
predict_next("the")
predict_next("cat")
predict_next("eats")
predict_next("on")
