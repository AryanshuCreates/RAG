from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import traceback

from .config import settings
from .models import QueryRequest, QueryResponse, IngestResponse
from .extractor import extract_text
from .chunker import chunk_many
from .embedder import embed_texts
from .store import store
from .rag import generate_answer

app = FastAPI(title="RAG Ingest Service", version="0.1.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    try:
        raw = await file.read()
        blocks = extract_text(raw, file.filename)
        chunks = chunk_many(blocks)
        embeddings = embed_texts([c["text"] for c in chunks])
        n = store.upsert(chunks, embeddings, source_filename=file.filename)
        return IngestResponse(status="ok", ingested_chunks=n, doc_name=file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    try:
        # retrieve similar chunks from vector store
        hits = store.query(req.question, k=2)

        # generate answer using LLM with retrieved context
        answer = generate_answer(req.question, hits)

        return QueryResponse(answer=answer, sources=hits)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
