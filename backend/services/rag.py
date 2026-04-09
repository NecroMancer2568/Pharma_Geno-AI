import os
from qdrant_client import QdrantClient, models

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "pharmacogenomics_kb"

def retrieve_clinical_guidelines(patient_embedding: list, top_k: int = 6) -> list:
    """
    Using the patient's embedding, performs a cosine similarity search 
    across the indexed Qdrant knowledge base.
    """
    try:
        client = QdrantClient(url=QDRANT_URL)
        
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=patient_embedding,
            limit=top_k
        )
        
        guidelines = []
        for res in results.points:
            payload = res.payload or {}
            guidelines.append({
                "gene": payload.get("gene"),
                "drug": payload.get("drug"),
                "evidence_level": payload.get("evidence_level"),
                "source": payload.get("source"),
                "text": payload.get("text")
            })
        return guidelines
        
    except Exception as e:
        print(f"RAG retrieval error: {e}")
        # Fallback for milestone if Qdrant isn't fully populated yet
        return []

def assemble_prompt(metabolizer_status: dict, guidelines: list) -> str:
    """
    Builds the structured prompt for Gemma 4.
    """
    profile_str = "\n".join([f"- {g}: {s}" for g, s in metabolizer_status.items()])
    
    guidelines_str = ""
    for i, g in enumerate(guidelines, 1):
        guidelines_str += f"[{i}] Source: {g.get('source')} | Gene: {g.get('gene')} | Drug: {g.get('drug')} | Evidence: {g.get('evidence_level')}\n"
        guidelines_str += f"{g.get('text')}\n\n"
        
    if not guidelines_str:
        guidelines_str = "No specific evidence-based guidelines retrieved. Proceed with standard clinical precautions based on metabolizer statuses."
        
    prompt = f"""You are a clinical pharmacogenomics AI assistant producing structured medical reports.
Your task is to analyze the patient's metabolizer statuses and the retrieved clinical guidelines, and output a JSON report.

PATIENT METABOLIZER STATUSES:
{profile_str}

RETRIEVED CLINICAL GUIDELINES:
{guidelines_str}

INSTRUCTIONS:
1. Output ONLY valid JSON.
2. The JSON must exactly match the following schema:
{{
  "overall_risk_score": <number 0-100>,
  "drug_compatibilities": [
    {{
      "drug_name": "<string>",
      "gene": "<string>",
      "compatibility_score": <number 0.0-1.0>,
      "risk_level": "<HIGH|MODERATE|LOW>",
      "recommendation": "<string>",
      "evidence_level": "<string>"
    }}
  ],
  "disease_risks": [],
  "ai_summary": "<string paragraph for physician>",
  "recommendations": ["<string action item 1>", "<string action item 2>"]
}}

Do not include markdown blocks like ```json in the output. Return raw JSON text.
"""
    return prompt
