import pytest
from unittest.mock import AsyncMock, MagicMock
from src.orchestrator import Orchestrator, ChatResponse
from src.retrieval.retriever import Retriever

@pytest.fixture
def mock_retriever():
    r = MagicMock(spec=Retriever)
    return r

@pytest.fixture
def mock_llm_client():
    client = MagicMock()
    client.generate = AsyncMock(return_value="Mocked Answer")
    return client

@pytest.mark.asyncio
async def test_orchestrator_out_of_scope(mock_retriever, mock_llm_client):
    orchestrator = Orchestrator(retriever=mock_retriever, llm_client=mock_llm_client)
    response = await orchestrator.answer("How many calories should I eat to lose weight?")
    
    assert response.refusal_type == "out_of_scope"
    assert "falls outside" in response.answer

@pytest.mark.asyncio
async def test_orchestrator_not_in_corpus(mock_retriever, mock_llm_client):
    mock_retriever.query.return_value = [
        {
            "metadata": {"doc_id": "test_doc"},
            "distance": 0.99  # Above the default 0.40 threshold
        }
    ]
    orchestrator = Orchestrator(retriever=mock_retriever, llm_client=mock_llm_client)
    response = await orchestrator.answer("What is the capital of France?")
    
    assert response.refusal_type == "not_in_corpus"
    assert "test_doc" in response.answer

@pytest.mark.asyncio
async def test_orchestrator_valid_query(mock_retriever, mock_llm_client):
    mock_retriever.query.return_value = [
        {
            "content": "Eat 5g of salt.",
            "distance": 0.20,
            "metadata": {
                "doc_id": "who-healthy-diet",
                "document_name": "Healthy Diet Fact Sheet",
                "publisher": "WHO",
                "year": 2024,
                "source_url": "http://who.int"
            }
        }
    ]
    
    orchestrator = Orchestrator(retriever=mock_retriever, llm_client=mock_llm_client)
    response = await orchestrator.answer("What does WHO recommend for daily salt intake?")
    
    assert response.refusal_type is None
    assert response.answer == "Mocked Answer"
    assert len(response.citations) == 1
    assert response.citations[0]["document_name"] == "Healthy Diet Fact Sheet"
    assert "who-healthy-diet" in response.documents_searched

@pytest.mark.asyncio
async def test_orchestrator_cross_document(mock_retriever, mock_llm_client):
    mock_retriever.query.return_value = [
        {
            "content": "Doc 1 text",
            "distance": 0.2,
            "metadata": {"doc_id": "doc1"}
        },
        {
            "content": "Doc 2 text",
            "distance": 0.3,
            "metadata": {"doc_id": "doc2"}
        }
    ]
    
    orchestrator = Orchestrator(retriever=mock_retriever, llm_client=mock_llm_client)
    response = await orchestrator.answer("Tell me about cooking oil")
    
    assert response.refusal_type is None
    assert "doc1" in response.documents_searched
    assert "doc2" in response.documents_searched
