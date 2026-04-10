import { JobStatus, GenomicReport } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  uploadFile: async (file: File, patientId: string): Promise<{ job_id: string; status: string; message: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('patient_id', patientId);

    const response = await fetch(`${API_BASE_URL}/api/upload/`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) throw new Error('Upload failed');
    return response.json();
  },

  getJobStatus: async (jobId: string): Promise<JobStatus> => {
    const response = await fetch(`${API_BASE_URL}/api/upload/status/${jobId}`);
    if (!response.ok) throw new Error('Failed to fetch job status');
    return response.json();
  },

  getReport: async (jobId: string): Promise<GenomicReport> => {
    const response = await fetch(`${API_BASE_URL}/api/reports/${jobId}`);
    if (!response.ok) throw new Error('Failed to fetch report');
    return response.json();
  },

  downloadPdf: (jobId: string) => {
    window.open(`${API_BASE_URL}/api/reports/${jobId}/pdf`, '_blank');
  }
};