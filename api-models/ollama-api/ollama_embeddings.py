import ollama

response = ollama.embed(
  model='embeddinggemma',
  input='Qual a cotação do dolar para hoje?',
)

embeddings = response['embeddings']
print(embeddings)