from typing import Iterable, List, Dict


DEFAULT_CHUNK_SIZE = 800 # characters
DEFAULT_CHUNK_OVERLAP = 120 # characters




def _split_paragraphs(text: str) -> List[str]:
    parts = [p.strip() for p in text.split("\n\n")]
    return [p for p in parts if p]




def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP) -> List[Dict]:
    """Simple char-based sliding window over concatenated paragraphs.
    Returns list of dicts: {"text": str, "start": int, "end": int}
    """
    if not text:
        return []
    paras = _split_paragraphs(text)
    joined = "\n\n".join(paras)


    chunks: List[Dict] = []
    n = len(joined)
    i = 0
    while i < n:
        end = min(i + chunk_size, n)
        chunk = joined[i:end]
        chunks.append({"text": chunk, "start": i, "end": end})
        if end == n:
            break
        i = max(end - overlap, 0)
    return chunks




def chunk_many(text_blocks: Iterable[str], **kw) -> List[Dict]:
    all_chunks: List[Dict] = []
    for blk in text_blocks:
        all_chunks.extend(chunk_text(blk, **kw))
    return all_chunks