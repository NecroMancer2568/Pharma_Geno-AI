"""
RAG Retriever for PharmGKB pharmacogenomic data using pgvector.
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass
import json

# Import will be available after pip install
try:
    import asyncpg
    from pgvector.asyncpg import register_vector
except ImportError:
    asyncpg = None


@dataclass
class PharmGKBEntry:
    gene: str
    rsid: str
    drug: str
    phenotype: str
    clinical_annotation: str
    evidence_level: str
    recommendation: str


# Embedded PharmGKB reference data for key drug-gene interactions
PHARMGKB_REFERENCE = {
    "CYP2D6": {
        "drugs": ["codeine", "tramadol", "oxycodone", "hydrocodone", "tamoxifen", "fluoxetine", "paroxetine", "venlafaxine", "amitriptyline", "nortriptyline"],
        "phenotypes": {
            "poor_metabolizer": "Significantly reduced enzyme activity. Prodrugs like codeine may be ineffective. Active drugs may accumulate.",
            "intermediate_metabolizer": "Reduced enzyme activity. May need dose adjustments.",
            "normal_metabolizer": "Normal enzyme activity. Standard dosing expected to be effective.",
            "ultrarapid_metabolizer": "Increased enzyme activity. Prodrugs may cause toxicity. Active drugs may be cleared too quickly."
        },
        "variants": {
            "rs3892097": {"allele": "*4", "effect": "non_functional"},
            "rs1065852": {"allele": "*10", "effect": "decreased_function"},
            "rs16947": {"allele": "*2", "effect": "normal_function"},
        }
    },
    "CYP2C19": {
        "drugs": ["clopidogrel", "omeprazole", "pantoprazole", "esomeprazole", "citalopram", "escitalopram", "sertraline", "voriconazole"],
        "phenotypes": {
            "poor_metabolizer": "Cannot activate clopidogrel effectively. Higher risk of cardiovascular events. PPIs may have prolonged effect.",
            "intermediate_metabolizer": "Reduced activation of clopidogrel. Consider alternative antiplatelet therapy.",
            "normal_metabolizer": "Normal drug metabolism expected.",
            "rapid_metabolizer": "May need higher doses of some medications.",
            "ultrarapid_metabolizer": "PPIs may be less effective. May need higher doses."
        },
        "variants": {
            "rs4244285": {"allele": "*2", "effect": "non_functional"},
            "rs4986893": {"allele": "*3", "effect": "non_functional"},
            "rs12248560": {"allele": "*17", "effect": "increased_function"},
        }
    },
    "CYP2C9": {
        "drugs": ["warfarin", "phenytoin", "celecoxib", "ibuprofen", "naproxen", "flurbiprofen", "losartan"],
        "phenotypes": {
            "poor_metabolizer": "Significantly reduced clearance of warfarin. High bleeding risk at standard doses.",
            "intermediate_metabolizer": "Reduced warfarin clearance. Lower starting dose recommended.",
            "normal_metabolizer": "Standard warfarin dosing expected to be appropriate."
        },
        "variants": {
            "rs1799853": {"allele": "*2", "effect": "decreased_function"},
            "rs1057910": {"allele": "*3", "effect": "decreased_function"},
        }
    },
    "VKORC1": {
        "drugs": ["warfarin", "acenocoumarol", "phenprocoumon"],
        "phenotypes": {
            "high_sensitivity": "Significantly increased warfarin sensitivity. Requires much lower doses.",
            "intermediate_sensitivity": "Moderately increased warfarin sensitivity. Lower doses may be needed.",
            "normal_sensitivity": "Standard warfarin dosing expected."
        },
        "variants": {
            "rs9923231": {"allele": "-1639G>A", "effect": "increased_sensitivity"},
        }
    },
    "SLCO1B1": {
        "drugs": ["simvastatin", "atorvastatin", "pravastatin", "rosuvastatin", "pitavastatin"],
        "phenotypes": {
            "poor_function": "High risk of statin-induced myopathy. Consider lower doses or alternative statins.",
            "intermediate_function": "Moderate risk of statin myopathy. Monitor closely.",
            "normal_function": "Standard statin dosing expected to be tolerable."
        },
        "variants": {
            "rs4149056": {"allele": "521T>C", "effect": "decreased_function"},
        }
    },
    "TPMT": {
        "drugs": ["azathioprine", "mercaptopurine", "thioguanine"],
        "phenotypes": {
            "poor_metabolizer": "Life-threatening myelosuppression risk at standard doses. Requires 90% dose reduction or alternative.",
            "intermediate_metabolizer": "Increased myelosuppression risk. Consider 50% dose reduction.",
            "normal_metabolizer": "Standard dosing expected to be tolerable."
        },
        "variants": {
            "rs1800460": {"allele": "*3A", "effect": "non_functional"},
            "rs1142345": {"allele": "*3C", "effect": "non_functional"},
        }
    },
    "DPYD": {
        "drugs": ["fluorouracil", "capecitabine", "tegafur"],
        "phenotypes": {
            "poor_metabolizer": "Life-threatening toxicity risk. Fluoropyrimidines contraindicated.",
            "intermediate_metabolizer": "Significantly increased toxicity risk. Major dose reduction required.",
            "normal_metabolizer": "Standard dosing expected."
        },
        "variants": {
            "rs3918290": {"allele": "*2A", "effect": "non_functional"},
            "rs55886062": {"allele": "*13", "effect": "non_functional"},
        }
    },
    "OPRM1": {
        "drugs": ["morphine", "fentanyl", "methadone", "naltrexone", "buprenorphine"],
        "phenotypes": {
            "reduced_response": "May require higher opioid doses for pain relief. Higher addiction risk with some alleles.",
            "normal_response": "Standard opioid dosing expected."
        },
        "variants": {
            "rs1799971": {"allele": "A118G", "effect": "reduced_binding"},
        }
    },
    "COMT": {
        "drugs": ["morphine", "codeine", "tramadol", "levodopa"],
        "phenotypes": {
            "low_activity": "Higher pain sensitivity. May need lower opioid doses but more frequently.",
            "intermediate_activity": "Moderate pain sensitivity.",
            "high_activity": "Lower pain sensitivity. May need higher doses."
        },
        "variants": {
            "rs4680": {"allele": "Val158Met", "effect": "variable"},
        }
    },
    "MTHFR": {
        "drugs": ["methotrexate", "folic_acid", "leucovorin"],
        "phenotypes": {
            "reduced_function": "Impaired folate metabolism. May need leucovorin supplementation with methotrexate.",
            "normal_function": "Standard dosing expected."
        },
        "variants": {
            "rs1801133": {"allele": "C677T", "effect": "decreased_function"},
            "rs1801131": {"allele": "A1298C", "effect": "decreased_function"},
        }
    },
}


class RAGRetriever:
    """
    Retrieves relevant pharmacogenomic data using embedded reference data
    and optionally pgvector for similarity search.
    """
    
    def __init__(self):
        self.db_pool = None
        self.reference_data = PHARMGKB_REFERENCE
    
    async def connect(self):
        """Connect to PostgreSQL with pgvector."""
        if asyncpg is None:
            return
        
        try:
            self.db_pool = await asyncpg.create_pool(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT", "5432")),
                user=os.getenv("POSTGRES_USER", "pharmgeno"),
                password=os.getenv("POSTGRES_PASSWORD", "pharmgeno_secret"),
                database=os.getenv("POSTGRES_DB", "pharmgeno_db"),
                min_size=2,
                max_size=10
            )
            async with self.db_pool.acquire() as conn:
                await register_vector(conn)
        except Exception as e:
            print(f"Warning: Could not connect to PostgreSQL: {e}")
            self.db_pool = None
    
    async def get_relevant_data(
        self,
        genetic_variants: Dict[str, Any],
        medications: List[str]
    ) -> Dict[str, Any]:
        """
        Get relevant pharmacogenomic data for the given variants and medications.
        Uses embedded reference data and optionally augments with pgvector search.
        """
        context = {
            "gene_drug_interactions": [],
            "variant_annotations": [],
            "phenotype_predictions": [],
            "clinical_recommendations": []
        }
        
        # Normalize medication names to lowercase
        medications_lower = [med.lower().strip() for med in medications]
        
        # Map variants to genes
        from core.dna_parser import PHARMGKB_RSIDS
        variant_genes = {}
        for rsid, variant in genetic_variants.items():
            gene = PHARMGKB_RSIDS.get(rsid.lower())
            if gene:
                if gene not in variant_genes:
                    variant_genes[gene] = []
                variant_genes[gene].append({
                    "rsid": rsid,
                    "genotype": variant.genotype
                })
        
        # Find relevant drug-gene interactions
        for gene, gene_data in self.reference_data.items():
            if gene not in variant_genes:
                continue
            
            # Check if any of the user's medications interact with this gene
            gene_drugs_lower = [d.lower() for d in gene_data["drugs"]]
            matching_drugs = [
                med for med in medications_lower 
                if any(drug in med or med in drug for drug in gene_drugs_lower)
            ]
            
            if matching_drugs:
                # Determine phenotype based on variants
                variants_info = variant_genes[gene]
                phenotype = self._predict_phenotype(gene, variants_info, gene_data)
                
                context["gene_drug_interactions"].append({
                    "gene": gene,
                    "drugs": matching_drugs,
                    "variants": variants_info,
                    "phenotype": phenotype,
                    "phenotype_description": gene_data["phenotypes"].get(phenotype, ""),
                    "all_affected_drugs": gene_data["drugs"]
                })
                
                context["phenotype_predictions"].append({
                    "gene": gene,
                    "predicted_phenotype": phenotype,
                    "description": gene_data["phenotypes"].get(phenotype, "Unknown phenotype")
                })
        
        # Add variant annotations
        for gene, variants in variant_genes.items():
            for var in variants:
                gene_data = self.reference_data.get(gene, {})
                variant_info = gene_data.get("variants", {}).get(var["rsid"], {})
                context["variant_annotations"].append({
                    "rsid": var["rsid"],
                    "gene": gene,
                    "genotype": var["genotype"],
                    "allele": variant_info.get("allele", "Unknown"),
                    "effect": variant_info.get("effect", "Unknown")
                })
        
        return context
    
    def _predict_phenotype(
        self,
        gene: str,
        variants: List[Dict],
        gene_data: Dict
    ) -> str:
        """
        Predict metabolizer phenotype based on variant genotypes.
        This is a simplified prediction model.
        """
        functional_alleles = 0
        non_functional_alleles = 0
        increased_function_alleles = 0
        
        for var in variants:
            rsid = var["rsid"]
            genotype = var["genotype"]
            
            variant_info = gene_data.get("variants", {}).get(rsid, {})
            effect = variant_info.get("effect", "normal_function")
            
            # Count alleles based on genotype (heterozygous vs homozygous)
            if len(genotype) == 2:
                for allele in genotype:
                    if effect == "non_functional":
                        non_functional_alleles += 1
                    elif effect == "decreased_function":
                        non_functional_alleles += 0.5
                    elif effect == "increased_function":
                        increased_function_alleles += 1
                    else:
                        functional_alleles += 1
        
        # Determine phenotype based on allele counts
        total_alleles = functional_alleles + non_functional_alleles + increased_function_alleles
        
        if total_alleles == 0:
            return "normal_metabolizer"
        
        if increased_function_alleles >= 2:
            return "ultrarapid_metabolizer"
        elif non_functional_alleles >= 1.5:
            return "poor_metabolizer"
        elif non_functional_alleles >= 0.5:
            return "intermediate_metabolizer"
        elif increased_function_alleles >= 1:
            return "rapid_metabolizer"
        else:
            return "normal_metabolizer"
