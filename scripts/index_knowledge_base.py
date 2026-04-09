import os
import sys
import yaml
from glob import glob

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, VectorParams, PointStruct
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Please run `pip install qdrant-client sentence-transformers PyYAML` first.")
    sys.exit(1)

KB_DIR = "backend/data/knowledge_base"
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "pharmacogenomics_kb"
MODEL_NAME = "all-MiniLM-L6-v2"  # 384 dimensions

def parse_markdown(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract YAML frontmatter
    parts = content.split("---")
    if len(parts) >= 3:
        try:
            frontmatter = yaml.safe_load(parts[1])
            body = "---".join(parts[2:]).strip()
            return frontmatter, body
        except Exception as e:
            print(f"Error parsing YAML in {filepath}: {e}")
    return None, None

def main():
    print(f"Loading embedding model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    print(f"Connecting to Qdrant at {QDRANT_URL}...")
    try:
        client = QdrantClient(url=QDRANT_URL)
        
        # Check if collection exists
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if COLLECTION_NAME not in collection_names:
            print(f"Creating collection '{COLLECTION_NAME}'...")
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
        else:
            print(f"Collection '{COLLECTION_NAME}' already exists.")
            
    except Exception as e:
        print(f"Failed to connect to Qdrant: {e}")
        print("Note: If Qdrant is not running, embeddings will be skipped.")
        return

    md_files = glob(os.path.join(KB_DIR, "*.md"))
    if not md_files:
        print(f"No markdown files found in {KB_DIR}")
        return
        
    print(f"Found {len(md_files)} documents. Generating embeddings and uploading...")
    points = []
    
    for i, file_path in enumerate(md_files):
        meta, text = parse_markdown(file_path)
        if not meta or not text:
            continue
            
        # Add text to metadata so we can retrieve it later
        meta["text"] = text
        
        # In a real app, chunking might be needed if text > 400 tokens. 
        # Here we assume files are pre-chunked (300-500 words).
        vector = model.encode(text).tolist()
        
        point = PointStruct(
            id=i+1,
            vector=vector,
            payload=meta
        )
        points.append(point)
        
        if len(points) >= 50:
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            points = []
            
    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        
    print("Indexing complete!")

if __name__ == "__main__":
    main()
