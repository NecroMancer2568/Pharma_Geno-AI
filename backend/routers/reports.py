from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
import os
from models.db import get_job
from models.schemas import GenomicReport
from services.audit import log_audit_event
from services.auth import get_current_user

router = APIRouter()

@router.get("/{job_id}", response_model=GenomicReport)
async def get_report(job_id: str, current_user: dict = Depends(get_current_user)):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["status"] != "complete":
        raise HTTPException(status_code=400, detail="Report not ready yet")
        
    log_audit_event("VIEW_REPORT", job["patient_id"], current_user.get("sub", "unknown"), f"Job: {job_id}")
    return GenomicReport(**job["result"])

@router.get("/{job_id}/pdf")
async def download_pdf(job_id: str, current_user: dict = Depends(get_current_user)):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job["status"] != "complete" or not job["result"]:
        raise HTTPException(status_code=400, detail="Report not ready yet")
        
    pdf_path = job["result"].get("pdf_path")
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found on server")
        
    log_audit_event("DOWNLOAD_PDF", job["patient_id"], current_user.get("sub", "unknown"), f"Job: {job_id}")
    return FileResponse(
        path=pdf_path, 
        media_type="application/pdf", 
        filename=f"Pharmacogenomics_Report_{job_id}.pdf"
    )
