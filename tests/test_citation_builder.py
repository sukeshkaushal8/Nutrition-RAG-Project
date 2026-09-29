import pytest
from src.generation.citation_builder import CitationBuilder

def test_citation_builder():
    builder = CitationBuilder()
    
    grouped_chunks = {
        "doc1": [
            {
                "content": "This is a long sentence explaining some complex dietary fact that we need to clip properly.",
                "metadata": {
                    "document_name": "Test Doc",
                    "publisher": "Test Pub",
                    "year": 2024,
                    "source_url": "http://example.com"
                }
            }
        ]
    }
    
    citations = builder.build(grouped_chunks)
    
    assert len(citations) == 1
    c = citations[0]
    
    assert c["document_name"] == "Test Doc"
    assert c["publisher"] == "Test Pub"
    assert c["year"] == 2024
    assert c["source_url"] == "http://example.com"
    assert "This is a long sentence" in c["chunk_excerpt"]

def test_citation_builder_empty():
    builder = CitationBuilder()
    citations = builder.build({"doc1": []})
    assert len(citations) == 0
