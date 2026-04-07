from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from dotenv import load_dotenv

load_dotenv()

from core.dna_parser import DNAParser
from core.rag_retriever import RAGRetriever
from core.report_generator import ReportGenerator

app = FastAPI(
    title="PharmGeno AI API",
    description="AI-powered pharmacogenomics platform for drug compatibility analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MedicationInput(BaseModel):
    medications: List[str]

class AnalysisResponse(BaseModel):
    overall_risk_score: int
    summary: str
    drugs: List[dict]
    gene_summary: List[dict]

dna_parser = DNAParser()
rag_retriever = RAGRetriever()
report_generator = ReportGenerator()


@app.get("/")
async def root():
    return {"message": "PharmGeno AI API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_dna(
    dna_file: UploadFile = File(...),
    medications: str = Form(...)
):
    """
    Analyze DNA file with provided medications and return drug compatibility report.
    
    - **dna_file**: 23andMe or AncestryDNA raw data file (.txt)
    - **medications**: JSON array of medication names
    """
    try:
        medication_list = json.loads(medications)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid medications format. Expected JSON array.")
    
    if not medication_list:
        raise HTTPException(status_code=400, detail="At least one medication is required.")
    
    # Parse DNA file
    content = await dna_file.read()
    dna_text = content.decode('utf-8', errors='replace')
    genetic_variants = await dna_parser.parse(dna_text)
    
    if not genetic_variants:
        raise HTTPException(status_code=400, detail="No valid genetic variants found in the uploaded file.")
    
    # Get relevant pharmacogenomic data via RAG
    pharmgkb_context = await rag_retriever.get_relevant_data(
        genetic_variants=genetic_variants,
        medications=medication_list
    )
    
    # Generate report using Claude
    report = await report_generator.generate(
        genetic_variants=genetic_variants,
        medications=medication_list,
        pharmgkb_context=pharmgkb_context
    )
    
    return report


@app.post("/api/analyze-demo", response_model=AnalysisResponse)
async def analyze_demo(medications: MedicationInput):
    """
    Demo endpoint using sample DNA data for demonstration purposes.
    """
    # Load sample demo data
    genetic_variants = await dna_parser.load_demo_data()
    
    # Get relevant pharmacogenomic data via RAG
    pharmgkb_context = await rag_retriever.get_relevant_data(
        genetic_variants=genetic_variants,
        medications=medications.medications
    )
    
    # Generate report using Claude
    report = await report_generator.generate(
        genetic_variants=genetic_variants,
        medications=medications.medications,
        pharmgkb_context=pharmgkb_context
    )
    
    return report


@app.get("/api/medications/search")
async def search_medications(q: str):
    """
    Search for medications using RxNorm API for autocomplete.
    """
    from core.rxnorm import search_medications
    results = await search_medications(q)
    return {"results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
