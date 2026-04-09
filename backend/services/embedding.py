import os
from sentence_transformers import SentenceTransformer

# Cache the model in memory so we don't load it per request
_MODEL = None

def get_embedding_model():
    global _MODEL
    if _MODEL is None:
        model_name = "all-MiniLM-L6-v2"
        _MODEL = SentenceTransformer(model_name)
    return _MODEL

def generate_patient_embedding(metabolizer_status: dict) -> list:
    """
    Converts the patient's full genomic profile into a text representation 
    and embeds using the local sentence-transformers model.
    """
    # Construct a clinical narrative of the patient's profile
    profile_text = "Patient Pharmacogenomic Profile:\n"
    for gene, status in metabolizer_status.items():
        if status != "Normal Metabolizer":
            profile_text += f"- {gene}: {status}\n"
            
    if profile_text == "Patient Pharmacogenomic Profile:\n":
        profile_text += "All evaluated pharmacogenes indicate Normal Metabolizer status."
        
    model = get_embedding_model()
    embedding = model.encode(profile_text).tolist()
    return embedding
