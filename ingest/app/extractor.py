import io
import pdfplumber
from typing import List


SUPPORTED_EXTS = {".pdf", ".txt"}




def _ext(name: str) -> str:
    n = name.lower()
    return n[n.rfind("."):] if "." in n else ""




def extract_text(file_bytes: bytes, filename: str) -> list[str]:
    """Return a list of raw text blocks (per-page for PDF, whole file for TXT)."""
    ext = _ext(filename)
    if ext not in SUPPORTED_EXTS:
        raise ValueError(f"Unsupported file type: {ext}")


    if ext == ".txt":
        return [file_bytes.decode("utf-8", errors="ignore")]


# PDF per-page extraction
    pages: List[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            txt = page.extract_text() or ""
            pages.append(txt)
    return pages