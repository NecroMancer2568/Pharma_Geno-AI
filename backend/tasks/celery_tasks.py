import os
import json
import asyncio
from datetime import datetime
from celery import Celery

# Explicit relative imports needed for Celery worker
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from models import db
from services.preprocessing import extract_pharmacogene_variants
from services.annotation import annotate_variant_clinvar, determine_metabolizer_status
from services.embedding import generate_patient_embedding
from services.rag import retrieve_clinical_guidelines, assemble_prompt
from services.llm import run_gemma_inference
from services.classifier import calculate_risk_scores
from services.report_generator import generate_pdf_report

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

celery_app = Celery("pharma_ai_tasks", broker=REDIS_URL)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"]
)

# Wrapper to run async LLM function in celery sync context
def run_async(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

@celery_app.task(name="process_genomic_file")
def process_genomic_file(job_id: str, file_path: str, patient_id: str):
    try:
        # Step 1
        db.update_job_progress(job_id, "processing", 5, "Parsing gene report")
        variants = extract_pharmacogene_variants(file_path)
        
        # Step 2
        db.update_job_progress(job_id, "processing", 15, "Extracting pharmacogene variants")
        
        # Step 3
        db.update_job_progress(job_id, "processing", 25, "Annotating variants with ClinVar")
        # For performance, only annotate the first 5 in the milestone
        for v in variants[:5]:
            run_async(annotate_variant_clinvar(v["rsid"]))
            
        # Step 4
        db.update_job_progress(job_id, "processing", 35, "Determining metabolizer status")
        metabolizer_status = determine_metabolizer_status(variants)
        
        # Step 5
        db.update_job_progress(job_id, "processing", 45, "Generating genomic embeddings")
        patient_embedding = generate_patient_embedding(metabolizer_status)
        
        # Step 6
        db.update_job_progress(job_id, "processing", 55, "Retrieving clinical guidelines (RAG)")
        guidelines = retrieve_clinical_guidelines(patient_embedding)
        
        # Step 7
        db.update_job_progress(job_id, "processing", 62, "Assembling clinical context")
        prompt = assemble_prompt(metabolizer_status, guidelines)
        
        # Step 8
        db.update_job_progress(job_id, "processing", 65, "Running Gemma 4 analysis")
        llm_report = run_async(run_gemma_inference(prompt))
        
        # Intermediate update post-LLM
        db.update_job_progress(job_id, "processing", 85, "Parsing Gemma 4 output")
        
        # Step 9
        db.update_job_progress(job_id, "processing", 90, "Calculating risk scores")
        risk_score = calculate_risk_scores(metabolizer_status)
        llm_report["overall_risk_score"] = risk_score
        llm_report["gene_activity_scores"] = metabolizer_status
        llm_report["job_id"] = job_id
        llm_report["patient_id"] = patient_id
        llm_report["created_at"] = datetime.now().isoformat()
        
        # Step 10
        db.update_job_progress(job_id, "processing", 95, "Generating PDF report")
        pdf_path = generate_pdf_report(job_id, llm_report)
        llm_report["pdf_path"] = pdf_path
        
        # Step 11
        db.update_job_progress(job_id, "complete", 100, "Complete", result=llm_report)
        
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return {"status": "success", "job_id": job_id}
        
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Job {job_id} failed: {error_msg}")
        db.update_job_progress(job_id, "failed", 0, "Failed", error=str(e))
        return {"status": "failed", "job_id": job_id, "error": str(e)}
