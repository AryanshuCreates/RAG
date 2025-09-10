from typing import List, Dict, Any
import uuid
from urllib.parse import urlparse
from chromadb import HttpClient
from .config import settings
from .embedder import embed_query


class VectorStore:
    def __init__(self):
        if settings.chroma_server_url:
            # parse host and port from CHROMA_URL
            parsed = urlparse(settings.chroma_server_url)
            host = parsed.hostname
            port = parsed.port or 8000
            self.client = HttpClient(host=host, port=port)
            print(f"[VectorStore] Using Chroma HTTP server at {host}:{port}")
        else:
            from chromadb import Client
            from chromadb.config import Settings as ChromaSettings
            persist_path = settings.persist_directory or "./chroma_data"
            self.client = Client(
                settings=ChromaSettings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory=persist_path,
                    is_persistent=True
                )
            )
            print(f"[VectorStore] Using local PersistentClient at {persist_path}")

        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name
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
        for i in range(len(res["ids"][0])):
            hits.append({
                "id": res["ids"][0][i],
                "score": 1 - res["distances"][0][i] if res.get("distances") else 0.0,
                "text": res["documents"][0][i],
                "metadata": res["metadatas"][0][i] or {},
            })
        return hits


store = VectorStore()
