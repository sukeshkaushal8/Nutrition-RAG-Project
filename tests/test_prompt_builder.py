import pytest
from src.generation.prompt_builder import PromptBuilder, SYSTEM_PROMPT

def test_prompt_builder_basic():
    builder = PromptBuilder()
    
    grouped_chunks = {
        "doc1": [
            {
                "content": "Apples are good.",
                "metadata": {
                    "document_name": "Fruit Facts",
                    "publisher": "Fruit Org",
                    "year": 2024
                }
            }
        ]
    }
    
    prompt = builder.build("Are apples good?", grouped_chunks)
    
    # System prompt is present
    assert SYSTEM_PROMPT.strip() in prompt
    
    # Source context is correctly formatted
    assert "Source 1: Fruit Facts (Fruit Org, 2024)" in prompt
    assert "URL: Unknown URL" in prompt
    assert "> Apples are good." in prompt
    
    # User query is present
    assert "--- User Question ---\nAre apples good?" in prompt

def test_prompt_builder_multiple_docs():
    builder = PromptBuilder()
    
    grouped_chunks = {
        "doc1": [
            {
                "content": "Apples are good.",
                "metadata": {
                    "document_name": "Fruit Facts",
                    "publisher": "Fruit Org",
                    "year": 2024
                }
            }
        ],
        "doc2": [
            {
                "content": "Bananas are also good.",
                "metadata": {
                    "document_name": "Banana Book",
                    "publisher": "Banana Co",
                    "year": 2023
                }
            }
        ]
    }
    
    prompt = builder.build("Tell me about fruits.", grouped_chunks)
    
    assert "Source 1: Fruit Facts (Fruit Org, 2024)" in prompt
    assert "> Apples are good." in prompt
    
    assert "Source 2: Banana Book (Banana Co, 2023)" in prompt
    assert "> Bananas are also good." in prompt

def test_prompt_builder_empty_chunks():
    builder = PromptBuilder()
    grouped_chunks = {"doc1": []}
    prompt = builder.build("Test?", grouped_chunks)
    assert "Source 1:" not in prompt
