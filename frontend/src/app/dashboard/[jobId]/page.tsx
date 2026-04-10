'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { JobStatus as JobStatusType, GenomicReport } from '@/lib/types';
import JobStatus from '@/components/JobStatus';
import RiskGauge from '@/components/RiskGauge';
import DrugCompatibilityTable from '@/components/DrugCompatibilityTable';
import DiseaseRiskPanel from '@/components/DiseaseRiskPanel';
import ReportExport from '@/components/ReportExport';
import { toast } from 'react-hot-toast';

export default function Dashboard({ params }: { params: { jobId: string } }) {
  const [job, setJob] = useState<JobStatusType | null>(null);
  const [report, setReport] = useState<GenomicReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const fetchStatus = async () => {
      try {
        const data = await api.getJobStatus(params.jobId);
        setJob(data);

        if (data.status === 'complete' && data.result) {
          setReport(data.result);
          clearInterval(interval);
          toast.success('Analysis complete!');
        } else if (data.status === 'failed') {
          setError(data.error || 'Job failed during processing');
          clearInterval(interval);
          toast.error('Analysis failed');
        }
      } catch (err: any) {
        console.error(err);
        setError('Failed to fetch job status');
        clearInterval(interval);
      }
    };

    fetchStatus();
    interval = setInterval(fetchStatus, 2000);

    return () => clearInterval(interval);
  }, [params.jobId]);

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-xl shadow-sm border border-red-200 text-center max-w-md">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Analysis Failed</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button 
            onClick={() => window.location.href = '/'}
            className="bg-gray-900 text-white px-6 py-2 rounded-lg hover:bg-gray-800 transition"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!job || job.status === 'pending' || job.status === 'processing') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <JobStatus progress={job?.progress || 0} currentStep={job?.current_step || 'Initializing...'} />
      </div>
    );
  }

  if (!report) return null;

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Clinical Pharmacogenomic Report</h1>
            <p className="text-gray-500 mt-1">Patient ID: {report.patient_id} • Job ID: {report.job_id.split('-')[0]}</p>
          </div>
          <ReportExport jobId={report.job_id} />
        </div>

        {/* Top Row: Risk & AI Summary */}
        <div className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-1">
            <RiskGauge score={report.overall_risk_score} />
          </div>
          <div className="md:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-blue-100 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1 h-full bg-blue-500" />
            <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <span className="text-blue-500">✨</span> AI Clinical Summary
            </h3>
            <p className="text-gray-700 leading-relaxed text-sm">
              {report.ai_summary}
            </p>
            <div className="mt-4 pt-4 border-t border-gray-100">
              <h4 className="text-sm font-semibold text-gray-800 mb-2">Key Recommendations:</h4>
              <ul className="list-disc list-inside text-sm text-gray-700 space-y-1 pl-4">
                {report.recommendations.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            </div>
            <p className="text-xs text-gray-400 mt-4 italic">
              Note: This summary is AI-generated and requires physician interpretation.
            </p>
          </div>
        </div>

        {/* Gene Activity Table */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-5 border-b border-gray-100">
            <h3 className="text-lg font-semibold text-gray-800">Gene Activity Profile</h3>
          </div>
          <div className="p-6 grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(report.gene_activity_scores).map(([gene, status]) => (
              <div key={gene} className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                <div className="font-bold text-gray-800 mb-1">{gene}</div>
                <div className={`text-sm font-medium ${
                  status.includes('Poor') || status.includes('Positive') ? 'text-red-600' :
                  status.includes('Intermediate') ? 'text-amber-600' :
                  status.includes('Rapid') ? 'text-blue-600' :
                  'text-green-600'
                }`}>
                  {status}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Drug & Disease Panels */}
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="lg:col-span-2">
             <DrugCompatibilityTable compatibilities={report.drug_compatibilities} />
          </div>
          <div className="lg:col-span-2">
             <DiseaseRiskPanel risks={report.disease_risks} />
          </div>
        </div>

      </div>
    </div>
  );
}