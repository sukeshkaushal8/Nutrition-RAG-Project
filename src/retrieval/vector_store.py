"""
Vector store wrapper — ChromaDB / Qdrant abstraction for storing
and querying embedded chunks.

Implemented in Phase 4.
"""

import logging
import chromadb
from src.config import settings

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="dietary_guidance",
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Initialized ChromaDB at {settings.chroma_persist_dir}")
        
    def add_chunks(self, chunks: list[dict], embeddings: list[list[float]]):
        """Add chunks and their embeddings to the vector store."""
        if not chunks:
            return
            
        ids = [chunk["chunk_id"] for chunk in chunks]
        documents = [chunk["content"] for chunk in chunks]
        
        # Prepare metadata
        metadatas = []
        for c in chunks:
            meta = {
                "doc_id": c.get("doc_id", ""),
                "document_name": c.get("document_name", ""),
                "publisher": c.get("publisher", ""),
                "year": int(c.get("year", 0)),
                "section_heading": c.get("section_heading", ""),
                "source_url": c.get("source_url", ""),
                "chunk_index": int(c.get("chunk_index", 0)),
                "token_count": int(c.get("token_count", 0))
            }
            metadatas.append(meta)
            
        # batching
        batch_size = 5000
        for i in range(0, len(ids), batch_size):
            self.collection.upsert(
                ids=ids[i:i+batch_size],
                documents=documents[i:i+batch_size],
                embeddings=embeddings[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size]
            )
        logger.info(f"Upserted {len(ids)} chunks to ChromaDB collection.")
        
    def count(self) -> int:
        return self.collection.count()
        
    def query(self, query_embeddings: list[list[float]], n_results: int = 8, where: dict = None):
        """Query the vector store using embeddings."""
        results = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where
        )
        return results
