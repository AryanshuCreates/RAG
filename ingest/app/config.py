import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env from project root (only matters for local dev)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))


class Settings(BaseModel):
    # Embeddings
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # Vector store / Chroma
    collection_name: str = os.getenv("COLLECTION_NAME", "rag_collection")
    chroma_server_url:str | None = os.getenv("CHROMA_SERVER_URL")  # e.g., http://chroma:8001 inside Docker
    persist_directory: str = os.getenv("CHROMA_DB_PATH", "./chroma_data")  # local fallback

    # Retrieval
    top_k: int = int(os.getenv("TOP_K", "5"))

    # Generation / LLM
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    max_context_chars: int = int(os.getenv("MAX_CONTEXT_CHARS", "8000"))


settings = Settings()
