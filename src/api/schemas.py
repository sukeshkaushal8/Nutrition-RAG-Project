from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str
    filter_document: Optional[str] = None
    top_k: int = 10

class CitationModel(BaseModel):
    document_name: str
    publisher: str
    year: int
    source_url: str
    chunk_excerpt: str

class ChatResponse(BaseModel):
    answer: str
    citations: List[CitationModel] = Field(default_factory=list)
    documents_searched: List[str] = Field(default_factory=list)
    refusal_type: Optional[str] = None

class DocumentRegistryEntry(BaseModel):
    doc_id: str
    title: str
    publisher: str
    year: int
    source_url: str
    retrieval_date: str
    format: str
    local_path: str
    category: str
