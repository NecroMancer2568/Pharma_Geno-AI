"""
Report Generator using Claude API for pharmacogenomic analysis.
"""

import os
import json
from typing import Dict, List, Any

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None


SYSTEM_PROMPT = """You are a pharmacogenomics expert AI assistant. Your task is to analyze genetic variants and medications to provide drug compatibility assessments.

CRITICAL RULES:
1. You MUST respond with ONLY valid JSON - no additional text, explanations, or markdown
2. Use ONLY the PharmGKB context data provided - do not hallucinate drug interactions
3. Be conservative with risk assessments - when uncertain, indicate moderate risk
4. Always recommend consulting healthcare providers for serious interactions

Your response MUST follow this exact JSON schema:
{
    "overall_risk_score": <integer 1-10, where 1=low risk, 10=high risk>,
    "summary": "<2-3 sentence plain English summary of key findings>",
    "drugs": [
        {
            "name": "<drug name>",
            "compatibility": "<safe|moderate_risk|high_risk|contraindicated>",
            "score": <integer 1-10>,
            "gene_variants_involved": ["<gene:variant list>"],
            "explanation": "<brief explanation>",
            "alternatives": ["<alternative drugs if any>"],
            "recommendation": "<specific dosing or monitoring recommendation>"
        }
    ],
    "gene_summary": [
        {
            "gene": "<gene name>",
            "phenotype": "<metabolizer status or sensitivity>",
            "clinical_significance": "<brief clinical impact>"
        }
    ]
}

Compatibility definitions:
- safe: No significant gene-drug interactions expected
- moderate_risk: Some interaction possible, monitoring recommended
- high_risk: Significant interaction likely, dose adjustment or alternative needed
- contraindicated: Drug should be avoided based on genetic profile

Score definitions:
- 1-3: Safe, minimal concerns
- 4-6: Moderate risk, proceed with caution
- 7-8: High risk, consider alternatives
- 9-10: Contraindicated or dangerous
"""


class ReportGenerator:
    """
    Generates pharmacogenomic compatibility reports using Gemini API.
    """
    
    def __init__(self):
        self.client = None
        self.model = "gemini-2.5-flash"
        
        if genai is not None:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                self.client = genai.Client(api_key=api_key)
    
    async def generate(
        self,
        genetic_variants: Dict[str, Any],
        medications: List[str],
        pharmgkb_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive drug compatibility report.
        """
        # Build the user prompt with all context
        user_prompt = self._build_prompt(genetic_variants, medications, pharmgkb_context)
        
        # If Gemini client is available, use it
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0,
                        response_mime_type="application/json",
                    ),
                )
                
                # Extract JSON from response
                response_text = response.text
                report = json.loads(response_text)
                return report
                
            except json.JSONDecodeError as e:
                print(f"Failed to parse Gemini response as JSON: {e}")
                return self._generate_fallback_report(medications, pharmgkb_context)
            except Exception as e:
                print(f"Gemini API error: {e}")
                return self._generate_fallback_report(medications, pharmgkb_context)
        else:
            # Fallback when Gemini is not available
            return self._generate_fallback_report(medications, pharmgkb_context)
    
    def _build_prompt(
        self,
        genetic_variants: Dict[str, Any],
        medications: List[str],
        pharmgkb_context: Dict[str, Any]
    ) -> str:
        """Build the user prompt with genetic and medication context."""
        
        # Format variants
        variants_text = "GENETIC VARIANTS DETECTED:\n"
        for rsid, variant in genetic_variants.items():
            gene = pharmgkb_context.get("variant_annotations", [])
            gene_name = next(
                (v["gene"] for v in gene if v["rsid"] == rsid),
                "Unknown"
            )
            variants_text += f"- {rsid} ({gene_name}): {variant.genotype}\n"
        
        # Format medications
        meds_text = "MEDICATIONS TO ANALYZE:\n"
        for med in medications:
            meds_text += f"- {med}\n"
        
        # Format PharmGKB context
        context_text = "PHARMGKB CONTEXT DATA:\n"
        
        if pharmgkb_context.get("gene_drug_interactions"):
            context_text += "\nGene-Drug Interactions:\n"
            for interaction in pharmgkb_context["gene_drug_interactions"]:
                context_text += f"- {interaction['gene']} affects: {', '.join(interaction['drugs'])}\n"
                context_text += f"  Phenotype: {interaction['phenotype']}\n"
                context_text += f"  Description: {interaction['phenotype_description']}\n"
        
        if pharmgkb_context.get("phenotype_predictions"):
            context_text += "\nPhenotype Predictions:\n"
            for pred in pharmgkb_context["phenotype_predictions"]:
                context_text += f"- {pred['gene']}: {pred['predicted_phenotype']}\n"
                context_text += f"  {pred['description']}\n"
        
        prompt = f"""Analyze the following genetic profile and medications for drug compatibility.

{variants_text}

{meds_text}

{context_text}

Based on this data, generate a comprehensive drug compatibility report in the required JSON format.
Remember: ONLY output valid JSON, no other text."""
        
        return prompt
    
    def _generate_fallback_report(
        self,
        medications: List[str],
        pharmgkb_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a fallback report when Gemini is not available.
        Uses the PharmGKB context to create a basic report.
        """
        drugs = []
        gene_summary = []
        max_risk = 1
        
        # Process gene-drug interactions from context
        interactions = pharmgkb_context.get("gene_drug_interactions", [])
        phenotypes = pharmgkb_context.get("phenotype_predictions", [])
        
        # Build gene summary
        for pred in phenotypes:
            phenotype = pred["predicted_phenotype"]
            significance = "Standard metabolism expected"
            
            if "poor" in phenotype:
                significance = "Reduced drug metabolism - dose adjustments may be needed"
            elif "ultrarapid" in phenotype:
                significance = "Increased drug metabolism - standard doses may be less effective"
            elif "intermediate" in phenotype:
                significance = "Slightly altered metabolism - monitoring recommended"
            
            gene_summary.append({
                "gene": pred["gene"],
                "phenotype": phenotype.replace("_", " ").title(),
                "clinical_significance": significance
            })
        
        # Process each medication
        for med in medications:
            med_lower = med.lower()
            drug_info = {
                "name": med,
                "compatibility": "safe",
                "score": 3,
                "gene_variants_involved": [],
                "explanation": "No significant pharmacogenomic interactions identified in your genetic profile.",
                "alternatives": [],
                "recommendation": "Standard dosing expected to be appropriate."
            }
            
            # Check if medication has interactions
            for interaction in interactions:
                if any(med_lower in d or d in med_lower for d in [drug.lower() for drug in interaction["drugs"]]):
                    phenotype = interaction["phenotype"]
                    gene = interaction["gene"]
                    
                    drug_info["gene_variants_involved"].append(f"{gene}:{phenotype}")
                    
                    # Set risk level based on phenotype
                    if "poor" in phenotype:
                        drug_info["compatibility"] = "high_risk"
                        drug_info["score"] = 7
                        drug_info["explanation"] = f"Your {gene} status ({phenotype.replace('_', ' ')}) significantly affects how you metabolize {med}."
                        drug_info["recommendation"] = "Consult your healthcare provider about dose adjustment or alternative medications."
                        max_risk = max(max_risk, 7)
                    elif "ultrarapid" in phenotype:
                        drug_info["compatibility"] = "moderate_risk"
                        drug_info["score"] = 5
                        drug_info["explanation"] = f"Your {gene} status ({phenotype.replace('_', ' ')}) may cause faster metabolism of {med}."
                        drug_info["recommendation"] = "May require higher doses or more frequent dosing. Discuss with your healthcare provider."
                        max_risk = max(max_risk, 5)
                    elif "intermediate" in phenotype:
                        drug_info["compatibility"] = "moderate_risk"
                        drug_info["score"] = 4
                        drug_info["explanation"] = f"Your {gene} status ({phenotype.replace('_', ' ')}) may moderately affect {med} metabolism."
                        drug_info["recommendation"] = "Standard dosing likely appropriate, but monitoring recommended."
                        max_risk = max(max_risk, 4)
            
            drugs.append(drug_info)
        
        # Generate summary
        high_risk_drugs = [d["name"] for d in drugs if d["compatibility"] == "high_risk"]
        moderate_risk_drugs = [d["name"] for d in drugs if d["compatibility"] == "moderate_risk"]
        
        if high_risk_drugs:
            summary = f"Your genetic profile indicates significant interactions with {', '.join(high_risk_drugs)}. "
            summary += "Consult your healthcare provider before taking these medications."
        elif moderate_risk_drugs:
            summary = f"Your genetic profile suggests moderate considerations for {', '.join(moderate_risk_drugs)}. "
            summary += "Standard precautions and monitoring are recommended."
        else:
            summary = "Your genetic profile does not indicate significant drug interactions with your current medications. "
            summary += "Standard dosing is expected to be appropriate."
        
        return {
            "overall_risk_score": max_risk,
            "summary": summary,
            "drugs": drugs,
            "gene_summary": gene_summary
        }
