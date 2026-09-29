"""
Orchestrator — ties scope check → retrieve → generate into a single pipeline.

Implemented in Phase 6.
"""

from typing import Optional
from dataclasses import dataclass
from src.config import settings
from src.retrieval.retriever import Retriever, group_by_document
from src.guardrails.scope_guard import is_out_of_scope
from src.guardrails.relevance_check import min_distance
from src.generation.llm_client import LLMClient
from src.generation.prompt_builder import PromptBuilder
from src.generation.citation_builder import CitationBuilder

@dataclass
class ChatResponse:
    answer: str
    citations: list[dict]
    documents_searched: list[str]
    refusal_type: Optional[str] = None

class Orchestrator:
    def __init__(self, retriever=None, llm_client=None):
        self.retriever = retriever or Retriever()
        self.llm_client = llm_client or LLMClient()
        self.prompt_builder = PromptBuilder()
        self.citation_builder = CitationBuilder()

    async def answer(self, query: str, filter_document: Optional[str] = None) -> ChatResponse:
        # 1. Scope check
        if is_out_of_scope(query):
            return ChatResponse(
                answer="This falls outside what I can help with. Please consult a qualified healthcare professional.",
                citations=[],
                documents_searched=[],
                refusal_type="out_of_scope"
            )

        # 2. Retrieve
        results = self.retriever.query(query, filter_doc=filter_document, top_k=settings.top_k)
        
        # Determine searched documents
        docs_searched = list(set(res["metadata"].get("doc_id", "unknown") for res in results))
        if not docs_searched and filter_document:
            docs_searched = [filter_document]

        # 3. Relevance check
        if min_distance(results) > settings.distance_threshold:
            searched_str = ", ".join(docs_searched) if docs_searched else "the whole corpus"
            return ChatResponse(
                answer=f"The dietary guidance documents I searched do not cover this topic. I searched: {searched_str}.",
                citations=[],
                documents_searched=docs_searched,
                refusal_type="not_in_corpus"
            )

        # 4. Group by document
        grouped = group_by_document(results)
        
        # 5. Build prompt
        prompt = self.prompt_builder.build(query, grouped)

        # 6. Generate
        try:
            raw_answer = await self.llm_client.generate(prompt)
        except Exception as e:
            return ChatResponse(
                answer=f"Sorry, I encountered an error communicating with the AI service: {str(e)}\n\n(Please ensure your GROQ_API_KEY is configured in the .env file)",
                citations=[],
                documents_searched=[],
                refusal_type="system_error"
            )

        # 7. Build citations
        citations = self.citation_builder.build(grouped)

        return ChatResponse(
            answer=raw_answer,
            citations=citations,
            documents_searched=list(grouped.keys()),
            refusal_type=None
        )
