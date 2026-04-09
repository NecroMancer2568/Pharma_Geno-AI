import os
import yaml

KB_DIR = "backend/data/knowledge_base"

# 13 pharmacogenes
GENES = ["CYP2D6", "CYP2C19", "CYP2C9", "CYP3A4", "CYP3A5", "DPYD", "TPMT", "VKORC1", "SLCO1B1", "UGT1A1", "NUDT15", "G6PD", "HLA-B"]
DRUGS = ["codeine", "clopidogrel", "warfarin", "tacrolimus", "simvastatin", "fluorouracil", "thiopurine", "irinotecan", "abacavir", "allopurinol"]

def generate_synthetic_kb():
    os.makedirs(KB_DIR, exist_ok=True)
    doc_id = 1
    
    print(f"Generating 200 synthetic markdown knowledge base documents in {KB_DIR}...")
    
    # Generate ~15 docs per gene
    for gene in GENES:
        for i in range(16):
            drug = DRUGS[i % len(DRUGS)]
            evidence = "1A" if i % 2 == 0 else "1B"
            source = "CPIC" if i % 3 == 0 else "PharmGKB"
            
            frontmatter = {
                "gene": gene,
                "drug": drug,
                "evidence_level": evidence,
                "source": source
            }
            
            content = f"""---
{yaml.dump(frontmatter, default_flow_style=False).strip()}
---

### Clinical Mechanism
The interaction between {gene} and {drug} has significant clinical implications. {gene} is primarily responsible for the metabolism of {drug}. 

### Clinical Consequence
Poor metabolizers of {gene} experience significantly altered systemic exposure to {drug}, leading to increased risk of toxicity or lack of efficacy. Normal metabolizers achieve standard therapeutic concentrations.

### CPIC Dosing Recommendation
For poor metabolizers, consider an alternative medication or a drastic dose reduction (e.g., 50%). For rapid/ultrarapid metabolizers, standard dosing may be inadequate, requiring close monitoring or alternative therapy.
"""
            file_path = os.path.join(KB_DIR, f"doc_{doc_id}_{gene}_{drug}.md")
            with open(file_path, "w") as f:
                f.write(content)
            
            doc_id += 1
            if doc_id > 205:
                break
        if doc_id > 205:
            break
            
    print(f"Generated {doc_id - 1} documents.")

if __name__ == "__main__":
    generate_synthetic_kb()
