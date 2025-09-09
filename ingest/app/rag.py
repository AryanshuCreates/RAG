from typing import List, Dict
import os
from .config import settings


# Optional OpenAI generator
try:
    from openai import OpenAI   
    _OPENAI_AVAILABLE = True
except Exception:
    _OPENAI_AVAILABLE = False




def build_context(hits: List[Dict], max_chars: int) -> str:
    ctx = []
    total = 0
    for h in hits:
        snippet = h["text"]
        add = snippet[: max(0, max_chars - total)]
        if not add:
            break
        ctx.append(f"[SOURCE: {h['metadata'].get('source','unknown')} @ {h['metadata'].get('start',0)}-{h['metadata'].get('end',0)}]\n{add}")
        total += len(add)
    return "\n\n".join(ctx)




def generate_answer(question: str, hits: List[Dict]) -> str:
# Use OpenAI if configured
    if settings.openai_api_key and _OPENAI_AVAILABLE:
        client = OpenAI(api_key=settings.openai_api_key)
        system = (
            "You are a helpful assistant. Answer the user's question using ONLY the provided context."
            " If the answer cannot be found in the context, say you don't know and suggest where to look."
            " Always cite sources inline like (source: <filename>)."
        )
        context = build_context(hits, settings.max_context_chars)
        user = f"Question: {question}\n\nContext:\n{context}"
        resp = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()


# Fallback: simple extractive-style answer (concatenate top chunks)
    context = build_context(hits, settings.max_context_chars)
    if not context:
        return "No relevant context found. Please ingest documents first."
    return (
        "(No LLM configured) Here are the most relevant excerpts from your documents.\n\n" + context
    )