import pytest
from pathlib import Path
from src.ingestion.parser import parse_html, parse_pdf, ParsedDocument, Section

def test_parse_html(tmp_path):
    html_content = """
    <html>
        <body>
            <h1>Main Title</h1>
            <p>This is a paragraph.</p>
            <h2>A List</h2>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
            <h2>A Table</h2>
            <table>
                <tr><th>H1</th><th>H2</th></tr>
                <tr><td>D1</td><td>D2</td></tr>
            </table>
        </body>
    </html>
    """
    html_file = tmp_path / "test.html"
    html_file.write_text(html_content, encoding="utf-8")
    
    metadata = {
        "doc_id": "test-html",
        "title": "Test Title",
        "publisher": "Test Pub",
        "year": 2024,
        "source_url": "http://test"
    }
    
    doc = parse_html(html_file, metadata)
    assert doc.doc_id == "test-html"
    
    # We expect 3 sections based on headings:
    # 1. Main Title (prose)
    # 2. A List (list)
    # 3. A Table (table)
    
    # wait, parser flushes when it encounters a new heading or specific tags depending on logic.
    # Let's check sections.
    headings = [s.heading for s in doc.sections]
    types = [s.section_type for s in doc.sections]
    
    assert "Test Title > Main Title" in headings
    assert "Test Title > Main Title > A List" in headings
    assert "Test Title > Main Title > A Table" in headings
    
    assert "prose" in types
    assert "list" in types
    assert "table" in types

def test_parser_models():
    doc = ParsedDocument(
        doc_id="a",
        title="b",
        publisher="c",
        year=2024,
        source_url="d",
        sections=[Section("h", "c", "prose")]
    )
    d = doc.to_dict()
    assert d["doc_id"] == "a"
    assert len(d["sections"]) == 1
