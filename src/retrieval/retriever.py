"""
Retriever module — query the vector store, apply metadata filters,
and group results by document for cross-document answers.

Implemented in Phase 5.
"""

from typing import Optional
from src.ingestion.embedder import Embedder
from src.retrieval.vector_store import VectorStore
from src.config import settings

class Retriever:
    def __init__(self, embedder: Embedder = None, vector_store: VectorStore = None):
        self.embedder = embedder or Embedder()
        self.vector_store = vector_store or VectorStore()

    def query(self, query_text: str, filter_doc: Optional[str] = None, top_k: Optional[int] = None) -> list[dict]:
        """
        Embed the query and retrieve chunks from the vector store using oversampling (fetch_k).
        Then filter them down by max_docs_in_answer and max_chunks_per_doc to get top_k.
        """
        if top_k is None:
            top_k = settings.top_k

        if not query_text.strip():
            return []

        # 1. Embed query
        query_emb = self.embedder.embed([query_text])[0]

        # 2. Prepare filter
        where = None
        if filter_doc:
            where = {"doc_id": filter_doc}

        # 3. Search vector store using fetch_k for diversity pool
        results = self.vector_store.query(
            query_embeddings=[query_emb],
            n_results=settings.fetch_k,
            where=where
        )

        # 4. Unpack results into a flat list of dictionaries
        if not results.get("ids") or not results["ids"][0]:
            return []

        ids = results["ids"][0]
        distances = results["distances"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        raw_results = []
        for i in range(len(ids)):
            raw_results.append({
                "chunk_id": ids[i],
                "content": documents[i],
                "distance": distances[i],
                "metadata": metadatas[i]
            })

        # 5. Apply Document and Chunk Caps for Diversity
        formatted_results = []
        doc_counts = {}
        distinct_docs_seen = 0
        
        for res in raw_results:
            doc_id = res["metadata"].get("doc_id", "unknown")
            
            # If we haven't seen this doc yet, check if we're at the document cap
            if doc_id not in doc_counts:
                if distinct_docs_seen >= settings.max_docs_in_answer:
                    continue # Skip chunk, we already have enough distinct documents
                distinct_docs_seen += 1
                doc_counts[doc_id] = 0
            
            # Check if this document has reached its chunk limit
            if doc_counts[doc_id] >= settings.max_chunks_per_doc:
                continue # Skip chunk, we have enough from this document
                
            formatted_results.append(res)
            doc_counts[doc_id] += 1
            
            if len(formatted_results) >= top_k:
                break

        return formatted_results

def group_by_document(results: list[dict]) -> dict[str, list[dict]]:
    """
    Group retrieved chunks by their source document (doc_id).
    Returns a dictionary mapping doc_id to a list of chunk dictionaries.
    """
    grouped = {}
    for res in results:
        doc_id = res["metadata"].get("doc_id", "unknown")
        if doc_id not in grouped:
            grouped[doc_id] = []
        grouped[doc_id].append(res)
    return grouped
