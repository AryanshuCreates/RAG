import os
from pydantic import BaseModel


class Settings(BaseModel):
    # Embeddings
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


    # Vector store / Chroma
    collection_name: str = os.getenv("COLLECTION", "rag_mvp")
    chroma_server_url: str | None = os.getenv("CHROMA_SERVER_URL") # e.g., http://chroma:8001
    persist_directory: str = os.getenv("PERSIST_DIR", "/data/chroma")


    # Retrieval
    top_k: int = int(os.getenv("TOP_K", "5"))


    # Generation
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    max_context_chars: int = int(os.getenv("MAX_CONTEXT_CHARS", "8000"))


settings = Settings()