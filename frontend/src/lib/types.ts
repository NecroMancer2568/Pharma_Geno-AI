export interface GenomicReport {
  job_id: string;
  patient_id: string;
  overall_risk_score: number;
  drug_compatibilities: DrugCompatibility[];
  disease_risks: DiseaseRisk[];
  gene_activity_scores: Record<string, string>;
  ai_summary: string;
  recommendations: string[];
  created_at: string;
  pdf_path: string;
}

export interface DrugCompatibility {
  drug_name: string;
  gene: string;
  compatibility_score: number;
  risk_level: 'HIGH' | 'MODERATE' | 'LOW';
  recommendation: string;
  evidence_level: string;
}

export interface DiseaseRisk {
  disease_name: string;
  risk_percentage: number;
  population_average: number;
  associated_genes: string[];
  risk_category: 'HIGH' | 'MODERATE' | 'LOW';
}

export interface JobStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'complete' | 'failed';
  progress: number;
  current_step: string;
  result: GenomicReport | null;
  error: string | null;
}