import httpx
import os
import redis
import json

# Redis connection for caching ClinVar API responses
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Known star alleles and their rsIDs based on CPIC guidelines
STAR_ALLELE_MAP = {
    "CYP2D6": {
        "rs3892097": {"allele": "*4", "function": "No function"},
        "rs35742686": {"allele": "*3", "function": "No function"},
        "rs5030655": {"allele": "*6", "function": "No function"}
    },
    "CYP2C19": {
        "rs4244285": {"allele": "*2", "function": "No function"},
        "rs4986893": {"allele": "*3", "function": "No function"},
        "rs12248560": {"allele": "*17", "function": "Increased function"}
    },
    "CYP2C9": {
        "rs1799853": {"allele": "*2", "function": "Decreased function"},
        "rs1057910": {"allele": "*3", "function": "No function"}
    },
    "DPYD": {
        "rs3918290": {"allele": "*2A", "function": "No function"},
        "rs67376798": {"allele": "c.2846A>T", "function": "Decreased function"}
    },
    "SLCO1B1": {
        "rs4149056": {"allele": "*5", "function": "Decreased function"}
    },
    "VKORC1": {
        "rs9923231": {"allele": "-1639G>A", "function": "Decreased warfarin dose requirement"}
    },
    "UGT1A1": {
        "rs3064744": {"allele": "*28", "function": "Decreased function"}
    },
    "HLA-B": {
        # Using a mock rsID for HLA-B*57:01 as HLA typing is complex in VCF
        "rs2395029": {"allele": "*57:01", "function": "Abacavir hypersensitivity"}
    },
    # Other genes will default to Normal Metabolizer if no target variant is found
    "CYP3A4": {},
    "CYP3A5": {},
    "TPMT": {},
    "NUDT15": {},
    "G6PD": {}
}

async def annotate_variant_clinvar(rsid: str) -> dict:
    """
    Cross-references a variant against ClinVar using Entrez E-utilities.
    Uses Redis caching to avoid rate limits (24h TTL).
    """
    if not rsid or rsid == ".":
        return {}
        
    cache_key = f"clinvar:{rsid}"
    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass
        
    api_key = os.getenv("NCBI_API_KEY", "")
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term={rsid}&retmode=json"
    if api_key:
        url += f"&api_key={api_key}"
        
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                id_list = data.get("esearchresult", {}).get("idlist", [])
                result = {
                    "rsid": rsid,
                    "clinvar_id": id_list[0] if id_list else None,
                    "annotated": bool(id_list)
                }
                try:
                    redis_client.setex(cache_key, 86400, json.dumps(result))
                except Exception:
                    pass
                return result
    except Exception as e:
        print(f"ClinVar API error for {rsid}: {e}")
        
    return {"rsid": rsid, "annotated": False}

def determine_metabolizer_status(variants: list) -> dict:
    """
    Assigns a metabolizer status for all 13 pharmacogenes based on variants.
    """
    # Initialize all genes to Normal Metabolizer
    status_map = {gene: "Normal Metabolizer" for gene in STAR_ALLELE_MAP.keys()}
    
    # Identify alleles present
    found_alleles = {gene: [] for gene in STAR_ALLELE_MAP.keys()}
    
    for v in variants:
        rsid = v.get("rsid")
        for gene, alleles in STAR_ALLELE_MAP.items():
            if rsid in alleles:
                found_alleles[gene].append(alleles[rsid])
                
    # Rule-based status assignment
    for gene, alleles in found_alleles.items():
        if not alleles:
            continue
            
        no_function_count = sum(1 for a in alleles if a["function"] == "No function")
        decreased_count = sum(1 for a in alleles if a["function"] == "Decreased function")
        increased_count = sum(1 for a in alleles if a["function"] == "Increased function")
        
        # Simple homozygous/heterozygous approximation for milestone
        if no_function_count >= 2:
            status_map[gene] = "Poor Metabolizer"
        elif no_function_count == 1:
            status_map[gene] = "Intermediate Metabolizer"
        elif decreased_count >= 2:
            status_map[gene] = "Poor Metabolizer"
        elif decreased_count == 1:
            status_map[gene] = "Intermediate Metabolizer"
        elif increased_count >= 1:
            status_map[gene] = "Rapid Metabolizer"
            
        if gene == "HLA-B" and alleles:
            status_map[gene] = "Positive for risk allele"
            
    return status_map
