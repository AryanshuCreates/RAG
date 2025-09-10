from chromadb import PersistentClient

class VectorStore:
    def __init__(self):
        # store vectors persistently in /data (mounted in docker-compose)
        self.client = PersistentClient(path="/data")
        self.collection = self.client.get_or_create_collection("rag_collection")

    def add(self, ids, embeddings, metadatas, documents):
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def query(self, query_embeddings, n_results=5):
        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results
        )

# singleton store instance
store = VectorStore()
