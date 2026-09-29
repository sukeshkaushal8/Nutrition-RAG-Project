import sys
import os

# Add project root to path so we can import src.config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieval.retriever import Retriever
from src.guardrails.relevance_check import min_distance

def main():
    retriever = Retriever()
    query = "healthy diet recommendations"
    results = retriever.query(query, top_k=5)
    
    print(f"Query: {query}")
    print("-" * 40)
    for res in results:
        print(f"Chunk ID: {res['chunk_id']}")
        print(f"Distance: {res['distance']:.4f}")
        print(f"Doc ID: {res['metadata']['doc_id']}")
        print(f"Content: {res['content'][:100]}...")
        print("-" * 40)
        
    md = min_distance(results)
    print(f"Min Distance: {md:.4f}")
    if md > 0.40:
        print("RESULT: Above threshold -> 'not in corpus' refusal")
    else:
        print("RESULT: Passed threshold")

    # Let's try an out of domain query
    print("\n")
    query2 = "what is the capital of France?"
    results2 = retriever.query(query2, top_k=5)
    print(f"Query: {query2}")
    print("-" * 40)
    for res in results2:
        print(f"Distance: {res['distance']:.4f}")
    md2 = min_distance(results2)
    print(f"Min Distance: {md2:.4f}")

if __name__ == "__main__":
    main()
