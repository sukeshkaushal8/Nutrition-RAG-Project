"""
Pipeline module — orchestrates the full ingestion flow:
scrape -> parse -> chunk -> embed -> store.

Implemented in Phase 4.
"""

import json
import glob
import logging
from src.ingestion.embedder import Embedder
from src.retrieval.vector_store import VectorStore

logger = logging.getLogger(__name__)

def embed_and_store_all():
    chunk_files = glob.glob("data/chunks/*.json")
    if not chunk_files:
        logger.warning("No chunk files found in data/chunks/")
        return
        
    embedder = Embedder()
    vector_store = VectorStore()
    
    for fpath in chunk_files:
        logger.info(f"Processing chunk file: {fpath}")
        with open(fpath, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            
        if not chunks:
            continue
            
        texts = [chunk["content"] for chunk in chunks]
        embeddings = embedder.embed(texts)
        vector_store.add_chunks(chunks, embeddings)
        
    logger.info(f"Embedding and storage complete. Total items in DB: {vector_store.count()}")
