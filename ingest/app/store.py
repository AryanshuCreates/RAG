from typing import List, Dict, Any
import uuid
from urllib.parse import urlparse
from chromadb import HttpClient, PersistentClient
from chromadb.config import Settings as ChromaSettings
from .config import settings
from .embedder import embed_query


class VectorStore:
    def __init__(self):
        if settings.chroma_server_url:
            # Use HTTP client for remote Chroma REST server
            parsed = urlparse(settings.chroma_server_url)
            host = parsed.hostname
            port = parsed.port or 8000
            self.client = HttpClient(host=host, port=port)
            print(f"[VectorStore] Using Chroma REST server at {host}:{port}")
        else:
            # Fallback to local PersistentClient
            persist_path = settings.persist_directory or "./chroma_data"
            self.client = PersistentClient(
                path=persist_path,
                settings=ChromaSettings(is_persistent=True)
            )
            print(f"[VectorStore] Using local Chroma PersistentClient at {persist_path}")

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"}  # Optional: index space
        )

    def upsert(self, chunks: List[Dict], embeddings: List[List[float]], source_filename: str) -> int:
        ids = [str(uuid.uuid4()) for _ in chunks]
        documents, metadatas = [], []

        for ch in chunks:
            documents.append(ch["text"])
            metadatas.append({
                "source": source_filename,
                "start": ch.get("start", 0),
                "end": ch.get("end", 0),
            })

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        return len(ids)

    def query(self, question: str, k: int) -> List[Dict[str, Any]]:
        qv = embed_query(question)
        res = self.collection.query(
            query_embeddings=[qv],
            n_results=k,
            include=["documents", "metadatas", "distances", "embeddings"]
        )
        hits: List[Dict[str, Any]] = []
        for i in range(len(res["ids"][0])):  # Chroma returns lists-of-lists
            hits.append({
                "id": res["ids"][0][i],
                "score": 1 - res["distances"][0][i] if res.get("distances") else 0.0,
                "text": res["documents"][0][i],
                "metadata": res["metadatas"][0][i] or {},
            })
        return hits


# Instantiate store
store = VectorStore()
