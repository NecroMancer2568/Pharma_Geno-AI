from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class DrugCompatibility(BaseModel):
    drug_name: str
    gene: str
    compatibility_score: float
    risk_level: str
    recommendation: str
    evidence_level: str

class DiseaseRisk(BaseModel):
    disease_name: str
    risk_percentage: float
    population_average: float
    associated_genes: List[str]
    risk_category: str

class GenomicReport(BaseModel):
    job_id: str
    patient_id: str
    overall_risk_score: float
    drug_compatibilities: List[DrugCompatibility]
    disease_risks: List[DiseaseRisk]
    gene_activity_scores: Dict[str, str]
    ai_summary: str
    recommendations: List[str]
    created_at: str
    pdf_path: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    current_step: str
    result: Optional[GenomicReport] = None
    error: Optional[str] = None
