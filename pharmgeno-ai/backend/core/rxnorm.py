"""
RxNorm API integration for medication name normalization and autocomplete.
"""

import httpx
from typing import List, Dict, Optional
from functools import lru_cache

RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST"


async def search_medications(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Search for medications using RxNorm API.
    Returns normalized drug names for autocomplete.
    """
    if not query or len(query) < 2:
        return []
    
    results = []
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Use approximateTerm for fuzzy matching
            response = await client.get(
                f"{RXNORM_BASE_URL}/approximateTerm.json",
                params={"term": query, "maxEntries": max_results}
            )
            
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("approximateGroup", {}).get("candidate", [])
                
                seen_names = set()
                for candidate in candidates:
                    rxcui = candidate.get("rxcui")
                    name = candidate.get("name", "").title()
                    score = candidate.get("score", 0)
                    
                    if name and name.lower() not in seen_names:
                        seen_names.add(name.lower())
                        results.append({
                            "rxcui": rxcui,
                            "name": name,
                            "score": score
                        })
                
                # Sort by score descending
                results.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    except httpx.TimeoutException:
        print("RxNorm API timeout - returning empty results")
    except Exception as e:
        print(f"RxNorm API error: {e}")
    
    return results[:max_results]


async def normalize_medication(name: str) -> Optional[Dict[str, str]]:
    """
    Normalize a medication name to its RxNorm standard form.
    """
    if not name:
        return None
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Find RxCUI for the medication name
            response = await client.get(
                f"{RXNORM_BASE_URL}/rxcui.json",
                params={"name": name, "search": 2}  # search=2 for normalized match
            )
            
            if response.status_code == 200:
                data = response.json()
                rxcui = data.get("idGroup", {}).get("rxnormId", [None])[0]
                
                if rxcui:
                    # Get properties for the RxCUI
                    props_response = await client.get(
                        f"{RXNORM_BASE_URL}/rxcui/{rxcui}/properties.json"
                    )
                    
                    if props_response.status_code == 200:
                        props = props_response.json().get("properties", {})
                        return {
                            "rxcui": rxcui,
                            "name": props.get("name", name).title(),
                            "synonym": props.get("synonym", ""),
                            "tty": props.get("tty", "")  # Term type
                        }
    
    except Exception as e:
        print(f"RxNorm normalization error: {e}")
    
    return {"name": name.title(), "rxcui": None}


async def get_drug_interactions(rxcui: str) -> List[Dict[str, str]]:
    """
    Get drug interactions for a medication using RxNorm.
    """
    interactions = []
    
    if not rxcui:
        return interactions
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{RXNORM_BASE_URL}/interaction/interaction.json",
                params={"rxcui": rxcui}
            )
            
            if response.status_code == 200:
                data = response.json()
                interaction_groups = data.get("interactionTypeGroup", [])
                
                for group in interaction_groups:
                    for interaction_type in group.get("interactionType", []):
                        for pair in interaction_type.get("interactionPair", []):
                            description = pair.get("description", "")
                            severity = pair.get("severity", "unknown")
                            
                            interacting_drug = None
                            for concept in pair.get("interactionConcept", []):
                                if concept.get("minConceptItem", {}).get("rxcui") != rxcui:
                                    interacting_drug = concept.get("minConceptItem", {}).get("name")
                            
                            if interacting_drug:
                                interactions.append({
                                    "drug": interacting_drug,
                                    "description": description,
                                    "severity": severity
                                })
    
    except Exception as e:
        print(f"RxNorm interaction check error: {e}")
    
    return interactions


# Common medications list for offline fallback
COMMON_MEDICATIONS = [
    "Acetaminophen", "Ibuprofen", "Aspirin", "Naproxen",
    "Omeprazole", "Pantoprazole", "Esomeprazole", "Lansoprazole",
    "Lisinopril", "Losartan", "Amlodipine", "Metoprolol", "Atenolol",
    "Metformin", "Glipizide", "Sitagliptin", "Empagliflozin",
    "Atorvastatin", "Simvastatin", "Rosuvastatin", "Pravastatin",
    "Sertraline", "Fluoxetine", "Escitalopram", "Citalopram", "Paroxetine",
    "Amoxicillin", "Azithromycin", "Ciprofloxacin", "Doxycycline",
    "Warfarin", "Clopidogrel", "Apixaban", "Rivaroxaban",
    "Gabapentin", "Pregabalin", "Tramadol", "Oxycodone", "Hydrocodone",
    "Levothyroxine", "Prednisone", "Albuterol", "Montelukast",
    "Tamoxifen", "Codeine", "Morphine", "Fentanyl",
    "Venlafaxine", "Duloxetine", "Bupropion", "Trazodone",
    "Azathioprine", "Mercaptopurine", "Methotrexate",
    "Fluorouracil", "Capecitabine"
]


def search_medications_offline(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Offline fallback for medication search using common medications list.
    """
    if not query or len(query) < 2:
        return []
    
    query_lower = query.lower()
    matches = [
        {"name": med, "rxcui": None, "score": 100 if med.lower().startswith(query_lower) else 50}
        for med in COMMON_MEDICATIONS
        if query_lower in med.lower()
    ]
    
    matches.sort(key=lambda x: (-x["score"], x["name"]))
    return matches[:max_results]
