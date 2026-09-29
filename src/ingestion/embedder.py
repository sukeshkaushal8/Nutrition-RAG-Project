"""
Embedder module — generates vector embeddings for text chunks using
sentence-transformers.

Implemented in Phase 4.
"""

import logging
from sentence_transformers import SentenceTransformer
from src.config import settings

logger = logging.getLogger(__name__)

class Embedder:
    def __init__(self):
        self.model_name = settings.embedding_model
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
    
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of text strings into vectors."""
        if not texts:
            return []
        
        logger.info(f"Embedding {len(texts)} texts...")
        # encode returns a numpy array, we need a list of lists of floats
        embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return embeddings.tolist()
