import sqlite3
import json
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pharma_ai.db").replace("sqlite:///", "")

def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            patient_id TEXT,
            status TEXT,
            progress INTEGER,
            current_step TEXT,
            result JSON,
            error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def create_job(job_id: str, patient_id: str):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO jobs (job_id, patient_id, status, progress, current_step)
        VALUES (?, ?, 'pending', 0, 'Job created')
    ''', (job_id, patient_id))
    conn.commit()
    conn.close()

def update_job_progress(job_id: str, status: str, progress: int, current_step: str, result: dict = None, error: str = None):
    conn = get_db()
    c = conn.cursor()
    
    result_str = json.dumps(result) if result else None
    
    c.execute('''
        UPDATE jobs 
        SET status = ?, progress = ?, current_step = ?, result = ?, error = ?
        WHERE job_id = ?
    ''', (status, progress, current_step, result_str, error, job_id))
    
    conn.commit()
    conn.close()

def get_job(job_id: str):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM jobs WHERE job_id = ?', (job_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        d = dict(row)
        if d['result']:
            d['result'] = json.loads(d['result'])
        return d
    return None

# Initialize db on module load
init_db()
