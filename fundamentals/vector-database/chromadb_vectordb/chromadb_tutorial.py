## https://docs.trychroma.com/docs/overview/getting-started

# Create a Chroma Client
import chromadb
chroma_client = chromadb.Client()

# Create a collection
collection = chroma_client.create_collection(name="my_collection")

# Add some text documents to the collection
# Uses the model: all-MiniLM-L6-v2
collection.add(
    ids=["id1", "id2"],
    documents=[
        "This is a document about pineapple",
        "This is a document about oranges"
    ]
)

# Query the collection
results = collection.query(
    query_texts=["Florida is the city of oranges"], # Chroma will embed this for you
    n_results=2 # how many results to return
)
print(results)
