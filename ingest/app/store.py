from chromadb import Client
from chromadb.config import Settings
from .config import settings
from .embedder import embed_query
import uuid

class VectorStore:
    def __init__(self):
        persist_path = settings.persist_directory or "./chroma_data"
        self.client = Client(
            settings=Settings(
                chroma_db_impl="duckdb+parquet",  # only supported mode
                persist_directory=persist_path,
                is_persistent=True
            )
        )
        print(f"[VectorStore] Using local PersistentClient at {persist_path}")

        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name
        )

    def upsert(self, chunks, embeddings, source_filename):
        ids = [str(uuid.uuid4()) for _ in chunks]
        documents = [ch["text"] for ch in chunks]
        metadatas = [
            {"source": source_filename, "start": ch.get("start", 0), "end": ch.get("end", 0)}
            for ch in chunks
        ]
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        return len(ids)

    def query(self, question, k):
        qv = embed_query(question)
        res = self.collection.query(
            query_embeddings=[qv],
            n_results=k,
            include=["documents", "metadatas", "distances", "embeddings"]
        )
        hits = []
        for i in range(len(res["ids"][0])):
            hits.append({
                "id": res["ids"][0][i],
                "score": 1 - res["distances"][0][i] if res.get("distances") else 0.0,
                "text": res["documents"][0][i],
                "metadata": res["metadatas"][0][i] or {},
            })
        return hits


store = VectorStore()
