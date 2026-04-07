'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowLeft, Download, AlertTriangle, CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import ReportCard from '@/components/ReportCard';
import RiskBadge from '@/components/RiskBadge';
import Disclaimer from '@/components/Disclaimer';

interface DrugReport {
  name: string;
  compatibility: 'safe' | 'moderate_risk' | 'high_risk' | 'contraindicated';
  score: number;
  gene_variants_involved: string[];
  explanation: string;
  alternatives: string[];
  recommendation: string;
}

interface GeneInfo {
  gene: string;
  phenotype: string;
  clinical_significance: string;
}

interface Report {
  overall_risk_score: number;
  summary: string;
  drugs: DrugReport[];
  gene_summary: GeneInfo[];
}

export default function ReportPage() {
  const router = useRouter();
  const [report, setReport] = useState<Report | null>(null);
  const [medications, setMedications] = useState<string[]>([]);

  useEffect(() => {
    const storedReport = sessionStorage.getItem('pharmgeno_report');
    const storedMedications = sessionStorage.getItem('pharmgeno_medications');
    
    if (storedReport) {
      setReport(JSON.parse(storedReport));
    } else {
      router.push('/upload');
    }
    
    if (storedMedications) {
      setMedications(JSON.parse(storedMedications));
    }
  }, [router]);

  if (!report) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full" />
      </div>
    );
  }

  const getRiskColor = (score: number) => {
    if (score <= 3) return 'text-green-400';
    if (score <= 6) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getRiskBg = (score: number) => {
    if (score <= 3) return 'bg-green-500/20';
    if (score <= 6) return 'bg-yellow-500/20';
    return 'bg-red-500/20';
  };

  return (
    <main className="min-h-screen px-6 py-12 lg:px-8">
      <div className="mx-auto max-w-4xl">
        {/* Medical Disclaimer - TOP OF PAGE, NON-DISMISSIBLE */}
        <Disclaimer prominent />

        {/* Header */}
        <div className="flex items-center justify-between mb-8 mt-8">
          <button
            onClick={() => router.push('/upload')}
            className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            New Analysis
          </button>
          
          <button
            onClick={() => window.print()}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg glass hover:bg-white/10 transition-all"
          >
            <Download className="w-5 h-5" />
            Export PDF
          </button>
        </div>

        {/* Overall Score */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`p-8 rounded-2xl ${getRiskBg(report.overall_risk_score)} mb-8`}
        >
          <div className="flex flex-col sm:flex-row items-center gap-6">
            <div className={`text-7xl font-bold ${getRiskColor(report.overall_risk_score)}`}>
              {report.overall_risk_score}
              <span className="text-2xl text-slate-400">/10</span>
            </div>
            <div className="flex-1 text-center sm:text-left">
              <h1 className="text-2xl font-bold mb-2">Overall Risk Score</h1>
              <p className="text-slate-300">{report.summary}</p>
            </div>
          </div>
        </motion.div>

        {/* Gene Summary */}
        {report.gene_summary.length > 0 && (
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-8"
          >
            <h2 className="text-xl font-bold mb-4">Your Genetic Profile</h2>
            <div className="grid sm:grid-cols-2 gap-4">
              {report.gene_summary.map((gene, index) => (
                <motion.div
                  key={gene.gene}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 + index * 0.05 }}
                  className="glass rounded-xl p-4"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-cyan-400 font-mono font-bold">{gene.gene}</span>
                    <span className="text-sm px-2 py-0.5 rounded-full bg-slate-700 text-slate-300">
                      {gene.phenotype}
                    </span>
                  </div>
                  <p className="text-sm text-slate-400">{gene.clinical_significance}</p>
                </motion.div>
              ))}
            </div>
          </motion.section>
        )}

        {/* Drug Reports */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-xl font-bold mb-4">Drug Compatibility Analysis</h2>
          <div className="space-y-4">
            {report.drugs.map((drug, index) => (
              <ReportCard key={drug.name} drug={drug} index={index} />
            ))}
          </div>
        </motion.section>

        {/* Footer Disclaimer */}
        <div className="mt-12 pt-8 border-t border-white/10">
          <p className="text-center text-slate-500 text-sm">
            Report generated on {new Date().toLocaleDateString()}. 
            This analysis is based on current pharmacogenomic research and may be updated as new evidence emerges.
          </p>
        </div>
      </div>
    </main>
  );
}
