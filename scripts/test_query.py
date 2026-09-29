import sys
from sentence_transformers import SentenceTransformer
from src.retrieval.vector_store import VectorStore

def main(query):
    model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    emb = model.encode([query], normalize_embeddings=True)[0].tolist()
    
    store = VectorStore()
    res = store.query([emb], n_results=3)
    
    print(f"Query: {query}")
    distances = res["distances"][0]
    docs = res["documents"][0]
    
    for i in range(len(distances)):
        print(f"Distance: {distances[i]:.4f}")
        print(f"Doc: {docs[i][:100]}...\n")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "What does the WHO recommend for daily salt intake?")
