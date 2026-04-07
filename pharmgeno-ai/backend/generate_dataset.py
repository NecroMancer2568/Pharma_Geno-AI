import os
import json
import asyncio
import random
import time
from core.report_generator import ReportGenerator
from dotenv import load_dotenv

# Make sure we find the .env file even if we run from another folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(ENV_PATH)

# === CONFIGURATION ===
OUTPUT_FILE = "pharmgeno_dataset.jsonl"
MOCK_PATIENT_COUNT = 1000 
SAVE_EVERY = 10 # Save checkpoints every 10 generations

# === MEDICAL KNOWLEDGE POOL (Expanded for maximal diversity) ===
# We want the model to see as many drugs/genes as possible.
GENES = ["CYP2C19", "CYP2D6", "CYP2C9", "CYP3A5", "CYP2B6", "SLCO1B1", "VKORC1", "DPYD", "TPMT"]
PHENOTYPES = ["poor_metabolizer", "intermediate_metabolizer", "normal_metabolizer", "ultrarapid_metabolizer", "rapid_metabolizer"]
PHENOTYPE_DESCRIPTIONS = {
    "poor_metabolizer": "Little to no enzyme activity. High risk of toxicity or low efficacy.",
    "intermediate_metabolizer": "Reduced enzyme activity. May require moderate dose changes.",
    "normal_metabolizer": "Standard enzyme activity. Standard dosing appropriate.",
    "ultrarapid_metabolizer": "Excessively high enzyme activity. Standard doses may fail.",
    "rapid_metabolizer": "Increased enzyme activity. Fast processing of medication."
}

# Real-world PGx Drugs
DRUGS = [
    "Clopidogrel", "Warfarin", "Simvastatin", "Codeine", "Amitriptyline", "Sertraline", 
    "Omeprazole", "Ibuprofen", "Tacrolimus", "Abacavir", "Allopurinol", "Phenytoin",
    "Carbamazepine", "Tramadol", "Paroxetine", "Fluvoxamine", "Escitalopram", "Citalopram"
]

RSIDS = ["rs12248560", "rs1057910", "rs9923231", "rs4149056", "rs2395029", "rs1799853"]
GENOTYPES = ["A/A", "G/G", "C/T", "T/T", "A/G", "C/C"]

async def generate_balanced_context():
    """Generates a randomized but medically plausible patient profile context."""
    num_genes = random.randint(1, 4)
    selected_genes = random.sample(GENES, num_genes)
    
    phenotype_predictions = []
    for gene in selected_genes:
        ptype = random.choice(PHENOTYPES)
        phenotype_predictions.append({
            "gene": gene,
            "predicted_phenotype": ptype,
            "description": PHENOTYPE_DESCRIPTIONS[ptype]
        })
    
    # Random variants
    variants = {}
    for _ in range(random.randint(1, 10)):
        rs = random.choice(RSIDS)
        variants[rs] = type('obj', (object,), {'genotype': random.choice(GENOTYPES)})()

    # Pick 1-3 random drugs
    meds = random.sample(DRUGS, random.randint(1, 3))
    
    # Fake some interactions to guide the AI
    interactions = []
    for med in meds:
        if random.random() > 0.5: # 50% chance of a mock interaction
            interactions.append({
                "gene": random.choice(selected_genes),
                "drugs": [med],
                "phenotype": random.choice(PHENOTYPES),
                "phenotype_description": "Clinical guidelines suggest monitoring or dose adjustment based on genetic profile."
            })

    return variants, meds, {"phenotype_predictions": phenotype_predictions, "gene_drug_interactions": interactions}

async def generate_dataset():
    generator = ReportGenerator()
    if not generator.client:
        print("ERROR: API key not found. Please add GEMINI_API_KEY to your .env file.")
        return

    # To handle crashes/resumes, check if file exists and how many lines it has
    start_from = 0
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            start_from = sum(1 for _ in f)
        print(f"Resuming from example {start_from}...")

    print(f"Goal: {MOCK_PATIENT_COUNT} examples total.")

    for i in range(start_from, MOCK_PATIENT_COUNT):
        variants, meds, context = await generate_balanced_context()
        
        try:
            prompt_text = generator._build_prompt(variants, meds, context)
            print(f"[{i+1}/{MOCK_PATIENT_COUNT}] Prompting AI for: {', '.join(meds)}...")
            
            # Using semaphore or sleep to avoid rate limits
            response_json = await generator.generate(variants, meds, context)
            
            # Save it
            with open(OUTPUT_FILE, "a") as f:
                f.write(json.dumps({
                    "prompt": prompt_text,
                    "ideal_json_response": json.dumps(response_json)
                }) + "\n")
                
            # Random sleep to mimic human interaction and bypass Gemini's Free-Tier RPS limits
            await asyncio.sleep(random.uniform(1.0, 3.0))

        except Exception as e:
            print(f"Error at {i}: {e}. Retrying in 10 seconds...")
            await asyncio.sleep(10)

    print(f"SUCCESS: Data generation complete. {OUTPUT_FILE} is ready for training.")

if __name__ == "__main__":
    asyncio.run(generate_dataset())
