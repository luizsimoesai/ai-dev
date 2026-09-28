import ollama

response = ollama.embed(
  model='embeddinggemma',
  input='What is the exchange rate for the dollar today?',
)

embeddings = response['embeddings']
print(embeddings)