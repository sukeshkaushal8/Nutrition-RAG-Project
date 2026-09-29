import pytest
from src.retrieval.retriever import Retriever, group_by_document

@pytest.fixture(scope="module")
def retriever():
    # Initializes Embedder and VectorStore using existing data in data/chroma
    return Retriever()

def test_retriever_query_basic(retriever):
    results = retriever.query("salt intake", top_k=5)
    
    assert len(results) <= 5
    assert len(results) > 0
    assert "chunk_id" in results[0]
    assert "distance" in results[0]
    assert "content" in results[0]
    assert "metadata" in results[0]

def test_retriever_filter_doc(retriever):
    results = retriever.query("salt", filter_doc="who-healthy-diet", top_k=5)
    
    assert len(results) > 0
    for res in results:
        assert res["metadata"]["doc_id"] == "who-healthy-diet"

def test_group_by_document():
    results = [
        {"metadata": {"doc_id": "doc1"}, "content": "foo"},
        {"metadata": {"doc_id": "doc2"}, "content": "bar"},
        {"metadata": {"doc_id": "doc1"}, "content": "baz"},
    ]
    
    grouped = group_by_document(results)
    
    assert len(grouped) == 2
    assert "doc1" in grouped
    assert "doc2" in grouped
    assert len(grouped["doc1"]) == 2
    assert len(grouped["doc2"]) == 1

def test_retriever_empty_query(retriever):
    results = retriever.query("")
    assert len(results) == 0
