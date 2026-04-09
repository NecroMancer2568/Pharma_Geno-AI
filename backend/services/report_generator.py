import os
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

REPORTS_DIR = os.getenv("REPORTS_DIR", "./data/reports")

def generate_pdf_report(job_id: str, report_data: dict) -> str:
    """
    Generates a PDF using ReportLab with built-in fonts only.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    pdf_path = os.path.join(REPORTS_DIR, f"{job_id}.pdf")
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Pharmacogenomics Clinical Report")
    
    # Header Info
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Job ID: {job_id}")
    c.drawString(50, height - 85, f"Overall Risk Score: {report_data.get('overall_risk_score', 0)}/100")
    
    # Summary
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 120, "AI Clinical Summary")
    c.setFont("Helvetica", 10)
    
    summary = report_data.get("ai_summary", "No summary available.")
    lines = simpleSplit(summary, "Helvetica", 10, width - 100)
    y = height - 135
    for line in lines:
        c.drawString(50, y, line)
        y -= 15
        
    # Recommendations
    y -= 15
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Recommendations")
    c.setFont("Helvetica", 10)
    y -= 15
    
    for idx, rec in enumerate(report_data.get("recommendations", []), 1):
        lines = simpleSplit(f"{idx}. {rec}", "Helvetica", 10, width - 100)
        for line in lines:
            c.drawString(50, y, line)
            y -= 15
            
    # Gene Activity
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Metabolizer Statuses")
    c.setFont("Helvetica", 10)
    y -= 15
    
    for gene, status in report_data.get("gene_activity_scores", {}).items():
        if status != "Normal Metabolizer":
            c.setFillColorRGB(0.8, 0, 0) if "Poor" in status or "Positive" in status else c.setFillColorRGB(0.8, 0.5, 0)
        else:
            c.setFillColorRGB(0, 0, 0)
            
        c.drawString(50, y, f"{gene}: {status}")
        y -= 15
        
        # Page break logic
        if y < 50:
            c.showPage()
            y = height - 50
            
    c.save()
    return pdf_path
