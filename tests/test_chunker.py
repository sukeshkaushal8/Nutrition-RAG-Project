import pytest
from src.ingestion.parser import ParsedDocument, Section
from src.ingestion.chunker import chunk_document, count_tokens, split_into_sentences

def test_split_into_sentences():
    text = "This is a sentence. And this is another! What about a third? Yes."
    sentences = split_into_sentences(text)
    assert len(sentences) == 4
    assert sentences[0] == "This is a sentence."
    assert sentences[1] == "And this is another!"

def test_table_atomicity():
    long_text = "word " * 600
    doc = ParsedDocument(
        doc_id="test",
        title="Test Doc",
        publisher="Test Pub",
        year=2024,
        source_url="http://test",
        sections=[Section(heading="A Table", content=long_text, section_type="table")]
    )
    chunks = chunk_document(doc)
    assert len(chunks) == 1
    assert chunks[0].content == f"[A Table]\n{long_text.strip()}"
    assert chunks[0].token_count > 512

def test_list_atomicity():
    long_text = "word " * 600
    doc = ParsedDocument(
        doc_id="test",
        title="Test Doc",
        publisher="Test Pub",
        year=2024,
        source_url="http://test",
        sections=[Section(heading="A List", content=long_text, section_type="list")]
    )
    chunks = chunk_document(doc)
    assert len(chunks) == 1
    assert chunks[0].content == f"[A List]\n{long_text.strip()}"

def test_prose_chunking():
    # 20 sentences, 50 words each => 1000 words. Should be split into 2-3 chunks.
    sentence = "Word " + "word " * 48 + "."
    text = (sentence + " ") * 20
    doc = ParsedDocument(
        doc_id="test",
        title="Test Doc",
        publisher="Test Pub",
        year=2024,
        source_url="http://test",
        sections=[Section(heading="Prose", content=text, section_type="prose")]
    )
    chunks = chunk_document(doc)
    assert len(chunks) > 1
    # Check max chunk tokens
    for c in chunks:
        assert c.token_count <= 512 + 100 # roughly, taking into account single sentence length and overlap

def test_metadata_propagation():
    doc = ParsedDocument(
        doc_id="test-doc-1",
        title="Test Title",
        publisher="Test Pub",
        year=2023,
        source_url="http://test.com",
        sections=[Section(heading="My Heading", content="Short content.", section_type="prose")]
    )
    chunks = chunk_document(doc)
    assert len(chunks) == 1
    c = chunks[0]
    assert c.doc_id == "test-doc-1"
    assert c.document_name == "Test Title"
    assert c.publisher == "Test Pub"
    assert c.year == 2023
    assert c.source_url == "http://test.com"
    assert c.section_heading == "My Heading"
    assert c.chunk_id == "test-doc-1__my-heading__0"
