"""
DNA Parser for 23andMe and AncestryDNA raw data files.
Supports streaming for large files (1M+ lines).
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import os


@dataclass
class GeneticVariant:
    rsid: str
    chromosome: str
    position: str
    genotype: str


# Key pharmacogenomic genes and their associated RSIDs
PHARMGKB_RSIDS = {
    # CYP2D6 - metabolizes ~25% of drugs
    "rs3892097": "CYP2D6",
    "rs1065852": "CYP2D6",
    "rs1800716": "CYP2D6",
    "rs16947": "CYP2D6",
    "rs1135840": "CYP2D6",
    
    # CYP2C19 - clopidogrel, PPIs, antidepressants
    "rs4244285": "CYP2C19",
    "rs4986893": "CYP2C19",
    "rs12248560": "CYP2C19",
    "rs28399504": "CYP2C19",
    
    # CYP2C9 - warfarin, NSAIDs
    "rs1799853": "CYP2C9",
    "rs1057910": "CYP2C9",
    
    # CYP3A4/CYP3A5 - statins, immunosuppressants
    "rs2740574": "CYP3A4",
    "rs776746": "CYP3A5",
    
    # VKORC1 - warfarin sensitivity
    "rs9923231": "VKORC1",
    "rs9934438": "VKORC1",
    
    # SLCO1B1 - statin myopathy
    "rs4149056": "SLCO1B1",
    
    # TPMT - thiopurines
    "rs1800460": "TPMT",
    "rs1142345": "TPMT",
    
    # DPYD - fluoropyrimidines
    "rs3918290": "DPYD",
    "rs55886062": "DPYD",
    
    # HLA-B - carbamazepine, abacavir
    "rs2395029": "HLA-B",
    
    # UGT1A1 - irinotecan
    "rs8175347": "UGT1A1",
    
    # Factor V Leiden
    "rs6025": "F5",
    
    # MTHFR - folate metabolism
    "rs1801133": "MTHFR",
    "rs1801131": "MTHFR",
    
    # OPRM1 - opioid response
    "rs1799971": "OPRM1",
    
    # COMT - pain medication
    "rs4680": "COMT",
    
    # APOE - statin response
    "rs429358": "APOE",
    "rs7412": "APOE",
}


class DNAParser:
    """Parse 23andMe and AncestryDNA raw data files with streaming support."""
    
    def __init__(self):
        self.relevant_rsids = set(PHARMGKB_RSIDS.keys())
    
    async def parse(self, dna_text: str) -> Dict[str, GeneticVariant]:
        """
        Parse DNA file content and extract pharmacogenomically relevant variants.
        Uses streaming approach for memory efficiency.
        """
        variants = {}
        
        for line in dna_text.split('\n'):
            # Skip comments and empty lines
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Parse tab or comma separated values
            parts = re.split(r'[\t,]', line)
            if len(parts) < 4:
                continue
            
            rsid = parts[0].strip().lower()
            
            # Only extract pharmacogenomically relevant variants
            if rsid in self.relevant_rsids or rsid.replace('rs', 'RS') in self.relevant_rsids:
                rsid_normalized = rsid.lower()
                variant = GeneticVariant(
                    rsid=rsid_normalized,
                    chromosome=parts[1].strip(),
                    position=parts[2].strip(),
                    genotype=parts[3].strip().upper()
                )
                variants[rsid_normalized] = variant
        
        return variants
    
    async def parse_streaming(self, file_path: str) -> Dict[str, GeneticVariant]:
        """
        Parse DNA file using streaming for memory efficiency with large files.
        """
        variants = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = re.split(r'[\t,]', line)
                if len(parts) < 4:
                    continue
                
                rsid = parts[0].strip().lower()
                
                if rsid in self.relevant_rsids:
                    variant = GeneticVariant(
                        rsid=rsid,
                        chromosome=parts[1].strip(),
                        position=parts[2].strip(),
                        genotype=parts[3].strip().upper()
                    )
                    variants[rsid] = variant
        
        return variants
    
    async def load_demo_data(self) -> Dict[str, GeneticVariant]:
        """
        Load sample demo data for demonstration purposes.
        Returns a representative set of pharmacogenomic variants.
        """
        demo_variants = {
            "rs4244285": GeneticVariant(rsid="rs4244285", chromosome="10", position="96541616", genotype="AG"),  # CYP2C19*2
            "rs12248560": GeneticVariant(rsid="rs12248560", chromosome="10", position="96521657", genotype="CT"),  # CYP2C19*17
            "rs3892097": GeneticVariant(rsid="rs3892097", chromosome="22", position="42526694", genotype="GA"),  # CYP2D6*4
            "rs1799853": GeneticVariant(rsid="rs1799853", chromosome="10", position="96702047", genotype="CT"),  # CYP2C9*2
            "rs1057910": GeneticVariant(rsid="rs1057910", chromosome="10", position="96741053", genotype="AA"),  # CYP2C9*3
            "rs9923231": GeneticVariant(rsid="rs9923231", chromosome="16", position="31107689", genotype="CT"),  # VKORC1
            "rs4149056": GeneticVariant(rsid="rs4149056", chromosome="12", position="21331549", genotype="TC"),  # SLCO1B1
            "rs1801133": GeneticVariant(rsid="rs1801133", chromosome="1", position="11856378", genotype="CT"),  # MTHFR
            "rs1799971": GeneticVariant(rsid="rs1799971", chromosome="6", position="154360797", genotype="AG"),  # OPRM1
            "rs4680": GeneticVariant(rsid="rs4680", chromosome="22", position="19963748", genotype="AG"),  # COMT
        }
        return demo_variants
    
    def get_gene_for_rsid(self, rsid: str) -> Optional[str]:
        """Get the gene name associated with an RSID."""
        return PHARMGKB_RSIDS.get(rsid.lower())
