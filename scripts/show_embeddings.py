import chromadb
import sys
import os

# Add project root to path so we can import src.config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import settings

def main():
    print(f"Connecting to ChromaDB at {settings.chroma_persist_dir}...")
    
    # Initialize the ChromaDB client
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    
    try:
        collection = client.get_collection(name="dietary_guidance")
    except Exception as e:
        print(f"Failed to get collection 'dietary_guidance': {e}")
        print("Existing collections:", client.list_collections())
        return

    count = collection.count()
    print(f"Collection 'dietary_guidance' has {count} total chunks/embeddings.")

    if count > 0:
        print("\nFetching a sample of 2 items...")
        # peek() returns a small sample of the collection
        results = collection.peek(limit=2)
        
        ids = results.get('ids', [])
        embeddings = results.get('embeddings', [])
        documents = results.get('documents', [])
        metadatas = results.get('metadatas', [])

        for i in range(len(ids)):
            print(f"\n" + "="*40)
            print(f"ITEM {i+1}")
            print(f"ID: {ids[i]}")
            
            # Print embedding shape and a small snippet
            emb = embeddings[i]
            print(f"Embedding length: {len(emb)} dimensions")
            print(f"Embedding snippet (first 5 vals): {emb[:5]}")
            
            # Print metadata
            print(f"\nMetadata:")
            for key, val in metadatas[i].items():
                print(f"  - {key}: {val}")
                
            # Print document excerpt
            doc_str = documents[i].replace('\n', ' ')
            print(f"\nDocument text (first 150 chars):\n\"{doc_str[:150]}...\"")
    else:
        print("The collection is currently empty.")

if __name__ == "__main__":
    main()
