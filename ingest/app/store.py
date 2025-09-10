from chromadb import PersistentClient
from .embedder import embed_texts

class VectorStore:
    def __init__(self):
        # Persistent vector DB in /data (docker-compose mounted)
        self.client = PersistentClient(path="/data")
        self.collection = self.client.get_or_create_collection("rag_collection")

    def upsert(self, chunks, embeddings, source_filename):
        ids = [f"{source_filename}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": source_filename, **c} for c in chunks]
        documents = [c["text"] for c in chunks]

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )
        return len(chunks)

    def query(self, query_text, k=5):
        # Convert query text into embeddings
        query_embedding = embed_texts([query_text])[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances", "ids"]
        )

        hits = []
        for i in range(len(results["ids"][0])):
            hits.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] or {},
                "distance": results["distances"][0][i]  # maps to the Pydantic model
            })
        return hits

# singleton
store = VectorStore()
