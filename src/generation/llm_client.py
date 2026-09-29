"""
LLM client — Groq API wrapper for answer generation.

Implemented in Phase 6.
"""

from groq import AsyncGroq
from src.config import settings

class LLMClient:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self.model = settings.llm_model
        
    async def generate(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model=self.model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )
        return response.choices[0].message.content
