import httpx
import os
import json

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
GEMMA_MODEL = os.getenv("GEMMA_MODEL", "gemma4:e2b")

async def run_gemma_inference(prompt: str) -> dict:
    """
    Sends prompt to local Gemma model via Ollama.
    Enforces JSON parsing and graceful fallback.
    """
    url = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": GEMMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1  # Clinical precision
        }
    }
    
    fallback_response = {
        "overall_risk_score": 50.0,
        "drug_compatibilities": [],
        "disease_risks": [],
        "ai_summary": "AI generation failed. Please rely on the tabular data.",
        "recommendations": ["Review metabolizer statuses manually."]
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                response_text = resp.json().get("response", "")
                
                # Try parsing JSON
                return extract_json_from_text(response_text)
            else:
                print(f"Ollama API error: {resp.status_code}")
                return fallback_response
    except Exception as e:
        print(f"LLM inference exception: {e}")
        return fallback_response

def extract_json_from_text(text: str) -> dict:
    """
    Attempts to extract JSON from LLM output.
    """
    fallback = {
        "overall_risk_score": 50.0,
        "drug_compatibilities": [],
        "disease_risks": [],
        "ai_summary": "Warning: Could not parse AI response perfectly. Partial data shown.",
        "recommendations": []
    }
    
    try:
        # Direct parse
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    try:
        # Search for JSON block
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end != 0:
            json_str = text[start:end]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
        
    return fallback
