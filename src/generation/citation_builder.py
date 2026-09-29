"""
Citation builder — formats inline citations from chunk metadata.

Implemented in Phase 6.
"""

class CitationBuilder:
    def build(self, grouped_chunks: dict[str, list[dict]]) -> list[dict]:
        citations = []
        for doc_id, chunks in grouped_chunks.items():
            if not chunks:
                continue
                
            first_meta = chunks[0]["metadata"]
            doc_name = first_meta.get("document_name", "Unknown")
            publisher = first_meta.get("publisher", "Unknown")
            year = first_meta.get("year", "Unknown")
            source_url = first_meta.get("source_url", "")
            
            chunk_content = chunks[0].get("content", "")
            chunk_excerpt = (chunk_content[:100] + "...") if len(chunk_content) > 100 else chunk_content
            
            citations.append({
                "document_name": doc_name,
                "publisher": publisher,
                "year": year,
                "source_url": source_url,
                "chunk_excerpt": chunk_excerpt
            })
        return citations
