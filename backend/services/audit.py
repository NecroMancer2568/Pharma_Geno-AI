import os
import logging
from datetime import datetime
from fastapi import Request

# Setup audit logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)
os.makedirs("data/logs", exist_ok=True)
fh = logging.FileHandler("data/logs/audit.log")
fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
audit_logger.addHandler(fh)

def log_audit_event(action: str, patient_id: str = "UNKNOWN", user_id: str = "UNKNOWN", details: str = ""):
    """
    Records data access events. Never logs raw genomic data.
    """
    # Anonymize patient_id slightly for the log if needed, or just log as-is per requirements
    # "Audit logs must record every data access event with timestamp, anonymized patient ID, and action type"
    masked_patient = f"PID-***{patient_id[-4:]}" if len(patient_id) > 4 else "PID-REDACTED"
    
    audit_message = f"USER:[{user_id}] ACTION:[{action}] PATIENT:[{masked_patient}] DETAILS:[{details}]"
    audit_logger.info(audit_message)
