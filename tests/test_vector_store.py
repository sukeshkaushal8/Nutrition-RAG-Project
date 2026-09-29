import pytest
from src.retrieval.vector_store import VectorStore
import chromadb

def test_vector_store_add_and_count(tmp_path, monkeypatch):
    import src.config
    monkeypatch.setattr(src.config.settings, "chroma_persist_dir", str(tmp_path))
    
    store = VectorStore()
    
    chunk = {
        "chunk_id": "test_chunk_1",
        "doc_id": "test_doc",
        "document_name": "Test Document",
        "publisher": "Test Pub",
        "year": 2026,
        "section_heading": "Test Section",
        "source_url": "http://test.com",
        "chunk_index": 0,
        "token_count": 10,
        "content": "This is a test chunk."
    }
    
    embedding = [[0.1] * 384]
    
    store.add_chunks([chunk], embedding)
    
    assert store.count() == 1
    
    # Query test
    results = store.query(query_embeddings=[[0.1] * 384], n_results=1)
    assert len(results["ids"][0]) == 1
    assert results["ids"][0][0] == "test_chunk_1"
