"""
Prompt builder — constructs prompts with system instructions,
grouped retrieved context, and the user query.

Implemented in Phase 6.
"""

SYSTEM_PROMPT = """You are a dietary guidance assistant. You answer questions about food,
nutrition, and food safety using ONLY the provided reference chunks.

RULES:
1. Answer ONLY from the provided chunks. Do not use prior knowledge.
2. Cite every claim with [Document Name, Publisher, Year](source_url).
3. When chunks from multiple documents are relevant, provide SEPARATE
   answers per document. NEVER blend sources into a single claim.
4. If the provided chunks do not contain the answer, say:
   "The dietary guidance documents I searched do not cover this topic.
    I searched: {list of documents searched}."
5. NEVER provide medical advice, calorie targets, weight-loss plans,
   or body-weight recommendations. If asked, respond:
   "This falls outside what I can help with. Please consult a
    qualified healthcare professional."
"""

class PromptBuilder:
    def build(self, query: str, grouped_chunks: dict[str, list[dict]]) -> str:
        prompt = f"{SYSTEM_PROMPT.strip()}\n\n--- Retrieved Context ---\n"
        
        source_index = 1
        for doc_id, chunks in grouped_chunks.items():
            if not chunks:
                continue
                
            first_meta = chunks[0]["metadata"]
            doc_name = first_meta.get("document_name", "Unknown")
            publisher = first_meta.get("publisher", "Unknown")
            year = first_meta.get("year", "Unknown")
            source_url = first_meta.get("source_url", "Unknown URL")
            
            prompt += f"Source {source_index}: {doc_name} ({publisher}, {year})\n"
            prompt += f"URL: {source_url}\n"
            for chunk in chunks:
                content = chunk.get("content", "").strip()
                prompt += f"> {content}\n"
            prompt += "\n"
            source_index += 1
            
        prompt += f"--- User Question ---\n{query}\n"
        return prompt
