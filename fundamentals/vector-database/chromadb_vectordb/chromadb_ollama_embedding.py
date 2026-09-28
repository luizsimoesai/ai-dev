import chromadb
from datetime import datetime
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

chroma_client = chromadb.Client()

ollama_ef = OllamaEmbeddingFunction(
    url="http://localhost:11434",
    model_name="embeddinggemma",
)

# example embedding creation
embeddings = ollama_ef(["This is my first text to embed",
                        "This is my second document"])


collection = chroma_client.create_collection(
    name="my_collection",
    embedding_function=ollama_ef,
    metadata={
        "description": "my first Chroma collection",
        "created": str(datetime.now())
    }
)

collections = chroma_client.list_collections()

collection = chroma_client.get_collection(
    name="my_collection",
    embedding_function=ollama_ef
)
