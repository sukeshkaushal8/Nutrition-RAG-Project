from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import json
import os
from src.api.schemas import ChatRequest, ChatResponse, DocumentRegistryEntry
from src.orchestrator import Orchestrator

router = APIRouter(prefix="/api/v1")
orchestrator = None

def get_orchestrator():
    global orchestrator
    if orchestrator is None:
        orchestrator = Orchestrator()
    return orchestrator

def load_registry() -> List[Dict[str, Any]]:
    registry_path = "data/corpus_registry.json"
    if not os.path.exists(registry_path):
        return []
    with open(registry_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("documents", [])

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    orch = get_orchestrator()
    response = await orch.answer(
        query=request.query, 
        filter_document=request.filter_document
    )
    return ChatResponse(
        answer=response.answer,
        citations=response.citations,
        documents_searched=response.documents_searched,
        refusal_type=response.refusal_type
    )

@router.get("/documents", response_model=List[DocumentRegistryEntry])
async def list_documents():
    registry = load_registry()
    return registry

@router.get("/documents/{doc_id}", response_model=DocumentRegistryEntry)
async def get_document(doc_id: str):
    registry = load_registry()
    for doc in registry:
        if doc["doc_id"] == doc_id:
            return doc
    raise HTTPException(status_code=404, detail="Document not found")

@router.post("/ingest")
async def ingest():
    import subprocess
    subprocess.Popen(["python", "scripts/ingest.py", "--step", "all"])
    return {"message": "Ingestion started"}

@router.get("/health")
async def health_check():
    return {"status": "ok"}
