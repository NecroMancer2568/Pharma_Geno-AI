'use client';

import { useState, useCallback, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, Pill, ArrowRight, X, Loader2 } from 'lucide-react';
import UploadZone from '@/components/UploadZone';
import MedicationInput from '@/components/MedicationInput';
import Disclaimer from '@/components/Disclaimer';

export default function UploadPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const isDemo = searchParams.get('demo') === 'true';
  
  const [step, setStep] = useState<'upload' | 'medications' | 'processing'>(isDemo ? 'medications' : 'upload');
  const [dnaFile, setDnaFile] = useState<File | null>(null);
  const [medications, setMedications] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = useCallback((file: File) => {
    setDnaFile(file);
    setError(null);
    setStep('medications');
  }, []);

  const handleAddMedication = useCallback((medication: string) => {
    if (!medications.includes(medication)) {
      setMedications(prev => [...prev, medication]);
    }
  }, [medications]);

  const handleRemoveMedication = useCallback((medication: string) => {
    setMedications(prev => prev.filter(m => m !== medication));
  }, []);

  const handleAnalyze = async () => {
    if (medications.length === 0) {
      setError('Please add at least one medication');
      return;
    }

    setIsLoading(true);
    setStep('processing');
    setError(null);

    try {
      let response;
      
      if (isDemo) {
        // Use demo endpoint
        response = await fetch('/api/analyze-demo', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ medications }),
        });
      } else {
        // Use file upload endpoint
        const formData = new FormData();
        formData.append('dna_file', dnaFile!);
        formData.append('medications', JSON.stringify(medications));
        
        response = await fetch('/api/analyze', {
          method: 'POST',
          body: formData,
        });
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const report = await response.json();
      
      // Store report in sessionStorage and navigate to report page
      sessionStorage.setItem('pharmgeno_report', JSON.stringify(report));
      sessionStorage.setItem('pharmgeno_medications', JSON.stringify(medications));
      router.push('/report');
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setStep('medications');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen px-6 py-12 lg:px-8">
      <div className="mx-auto max-w-3xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-3xl sm:text-4xl font-bold mb-4">
            {isDemo ? 'Try Demo Analysis' : 'Analyze Your DNA'}
          </h1>
          <p className="text-slate-400">
            {isDemo 
              ? 'Using sample genetic data for demonstration'
              : 'Upload your 23andMe or AncestryDNA file'
            }
          </p>
        </motion.div>

        {/* Progress Steps */}
        <div className="flex justify-center gap-4 mb-12">
          {[
            { id: 'upload', label: 'DNA File', icon: Upload },
            { id: 'medications', label: 'Medications', icon: Pill },
            { id: 'processing', label: 'Analysis', icon: FileText }
          ].map((s, index) => (
            <div key={s.id} className="flex items-center">
              <div className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${
                step === s.id 
                  ? 'bg-cyan-500/20 text-cyan-400' 
                  : (index < ['upload', 'medications', 'processing'].indexOf(step) || (isDemo && s.id === 'upload'))
                    ? 'bg-green-500/20 text-green-400'
                    : 'bg-slate-700/50 text-slate-500'
              }`}>
                <s.icon className="w-4 h-4" />
                <span className="text-sm font-medium hidden sm:inline">{s.label}</span>
              </div>
              {index < 2 && <ArrowRight className="w-4 h-4 text-slate-600 mx-2" />}
            </div>
          ))}
        </div>

        {/* Error Message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-center"
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Step Content */}
        <AnimatePresence mode="wait">
          {step === 'upload' && !isDemo && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <UploadZone onFileUpload={handleFileUpload} />
            </motion.div>
          )}

          {step === 'medications' && (
            <motion.div
              key="medications"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              {!isDemo && dnaFile && (
                <div className="mb-6 p-4 rounded-xl bg-green-500/10 border border-green-500/20 flex items-center gap-3">
                  <FileText className="w-5 h-5 text-green-400" />
                  <span className="text-green-400">{dnaFile.name}</span>
                </div>
              )}
              
              <MedicationInput
                medications={medications}
                onAdd={handleAddMedication}
                onRemove={handleRemoveMedication}
              />

              <div className="mt-8 flex justify-center">
                <button
                  onClick={handleAnalyze}
                  disabled={medications.length === 0}
                  className="inline-flex items-center gap-2 px-8 py-4 text-lg font-semibold rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-cyan-500/25"
                >
                  Analyze Compatibility
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            </motion.div>
          )}

          {step === 'processing' && (
            <motion.div
              key="processing"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-16"
            >
              <div className="inline-flex p-6 rounded-full bg-cyan-500/10 mb-6">
                <Loader2 className="w-12 h-12 text-cyan-400 animate-spin" />
              </div>
              <h2 className="text-2xl font-bold mb-2">Analyzing Your Profile</h2>
              <p className="text-slate-400 mb-8">
                Processing genetic variants and checking drug interactions...
              </p>
              <div className="flex justify-center gap-2">
                {[0, 1, 2].map(i => (
                  <motion.div
                    key={i}
                    className="w-3 h-3 rounded-full bg-cyan-400"
                    animate={{ scale: [1, 1.5, 1] }}
                    transition={{ duration: 0.6, delay: i * 0.2, repeat: Infinity }}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Disclaimer */}
        <div className="mt-12">
          <Disclaimer />
        </div>
      </div>
    </main>
  );
}
