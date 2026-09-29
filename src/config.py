"""
Centralised configuration using Pydantic Settings.

All values can be overridden via environment variables or a `.env` file
located at the project root.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    # ── LLM ──────────────────────────────────────────────────────────
    groq_api_key: str = ""
    llm_model: str = "openai/gpt-oss-20b"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1024

    # ── Embedding ────────────────────────────────────────────────────
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # ── Vector Store ─────────────────────────────────────────────────
    vector_store_type: str = "chroma"
    chroma_persist_dir: str = "./data/chroma"
    qdrant_url: str = "http://localhost:6333"

    # ── Retrieval ────────────────────────────────────────────────────
    fetch_k: int = 30
    top_k: int = 10
    distance_threshold: float = 0.40
    max_docs_in_answer: int = 3
    max_chunks_per_doc: int = 4

    # ── Server ───────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance — import this where needed
settings = Settings()
