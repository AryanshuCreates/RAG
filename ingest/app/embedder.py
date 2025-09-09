from sentence_transformers import SentenceTransformer
from functools import lru_cache
from typing import List
from .config import settings


@lru_cache(maxsize=1)
def _model():
    return SentenceTransformer(settings.embedding_model)




def embed_texts(texts: List[str]) -> List[List[float]]:
    model = _model()
    return [v.tolist() for v in model.encode(texts, show_progress_bar=False, normalize_embeddings=True)]




def embed_query(text: str) -> List[float]:
    model = _model()
    v = model.encode([text], show_progress_bar=False, normalize_embeddings=True)[0]
    return v.tolist()