import os
import uuid
import shutil
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from models.db import create_job, get_job
from tasks.celery_tasks import process_genomic_file
from models.schemas import JobStatusResponse
from services.audit import log_audit_event
from services.auth import get_current_user

router = APIRouter()
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def check_magic_bytes(file_path: str) -> bool:
    with open(file_path, "rb") as f:
        header = f.read(4)
        
    # GZIP magic bytes for .vcf.gz
    if header.startswith(b"\\x1f\\x8b"):
        return True
    
    # Simple text/vcf check (often starts with "##fileformat=VCF")
    if header.startswith(b"##fi") or header.startswith(b"#"):
         return True
         
    # Fallback for plain text like 23andme or FASTA
    try:
        header.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False

@router.post("/", response_model=dict)
async def upload_file(
    patient_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    valid_extensions = [".vcf", ".vcf.gz", ".txt", ".tsv", ".fasta"]
    if not any(file.filename.lower().endswith(ext) for ext in valid_extensions):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")
    
    file_size = 0
    with open(file_path, "wb") as buffer:
        while chunk := file.file.read(8192):
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                os.remove(file_path)
                raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")
            buffer.write(chunk)
            
    # Validate magic bytes
    if not check_magic_bytes(file_path):
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Invalid file content type (magic bytes mismatch)")
        
    # Log audit event
    log_audit_event("UPLOAD_REPORT", patient_id, current_user.get("sub", "unknown"), f"File: {file.filename}, Size: {file_size}")

    # Create DB record
    create_job(job_id, patient_id)
    
    # Dispatch Celery task
    process_genomic_file.delay(job_id, file_path, patient_id)
    
    return {"job_id": job_id, "status": "processing", "message": "File uploaded and job started"}

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_upload_status(job_id: str, current_user: dict = Depends(get_current_user)):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return JobStatusResponse(**job)
