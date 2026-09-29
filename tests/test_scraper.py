import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from src.ingestion.scraper import download_file, _create_fallback_file, scrape_all

def test_create_fallback_html():
    with tempfile.TemporaryDirectory() as tmpdir:
        dest_path = os.path.join(tmpdir, "test.html")
        _create_fallback_file(dest_path, "html")
        
        assert os.path.exists(dest_path)
        with open(dest_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "<html>" in content

def test_create_fallback_pdf():
    with tempfile.TemporaryDirectory() as tmpdir:
        dest_path = os.path.join(tmpdir, "test.pdf")
        _create_fallback_file(dest_path, "pdf")
        
        assert os.path.exists(dest_path)
        with open(dest_path, "rb") as f:
            content = f.read()
            assert content.startswith(b"%PDF")

@patch("src.ingestion.scraper.requests.get")
def test_download_file_success(mock_get):
    mock_response = MagicMock()
    mock_response.content = b"<html>Success</html>"
    mock_response.headers = {"Content-Type": "text/html"}
    mock_get.return_value = mock_response
    
    with tempfile.TemporaryDirectory() as tmpdir:
        dest_path = os.path.join(tmpdir, "success.html")
        download_file("http://example.com", dest_path, "html")
        
        assert os.path.exists(dest_path)
        with open(dest_path, "rb") as f:
            assert f.read() == b"<html>Success</html>"

@patch("src.ingestion.scraper.requests.get")
def test_download_file_fallback_on_error(mock_get):
    mock_get.side_effect = Exception("Network error")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        dest_path = os.path.join(tmpdir, "error.html")
        download_file("http://example.com/fail", dest_path, "html")
        
        assert os.path.exists(dest_path)
        with open(dest_path, "r", encoding="utf-8") as f:
            assert "Fallback Content" in f.read()

@patch("src.ingestion.scraper.download_file")
def test_scrape_all(mock_download_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = os.path.join(tmpdir, "registry.json")
        registry_data = {
            "documents": [
                {
                    "doc_id": "doc1",
                    "source_url": "http://example.com/doc1",
                    "local_path": "data/raw/doc1.html",
                    "format": "html"
                }
            ]
        }
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(registry_data, f)
            
        scrape_all(registry_path)
        mock_download_file.assert_called_once_with("http://example.com/doc1", "data/raw/doc1.html", "html")
