from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    question: str

class SourceChunk(BaseModel):
    id: str
    distance: float   # changed from score to distance
    text: str
    metadata: dict

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]

class IngestResponse(BaseModel):
    status: str
    ingested_chunks: int
    doc_name: str
