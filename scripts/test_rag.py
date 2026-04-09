import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

try:
    from qdrant_client import QdrantClient
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Please install requirements first.")
    sys.exit(1)

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "pharmacogenomics_kb"
MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    query = "CYP2D6 codeine"
    
    print(f"Loading embedding model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    try:
        client = QdrantClient(url=QDRANT_URL)
    except Exception as e:
        print(f"Could not connect to Qdrant: {e}")
        return

    print(f"Searching Qdrant for: '{query}'...")
    query_vector = model.encode(query).tolist()
    
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=3
    )
    
    if not results:
        print("No results found. Is the collection populated?")
        return
        
    print("\nTop 3 Results:")
    for i, res in enumerate(results, 1):
        payload = res.payload or {}
        print(f"\nResult {i} (Score: {res.score:.4f})")
        print(f"Gene: {payload.get('gene')} | Drug: {payload.get('drug')} | Source: {payload.get('source')}")
        text = payload.get('text', '')
        # Print first 150 chars of text
        print(f"Text snippet: {text[:150]}...")

if __name__ == "__main__":
    main()
