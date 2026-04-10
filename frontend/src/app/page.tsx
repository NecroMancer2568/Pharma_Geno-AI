'use client';

import { useRouter } from 'next/navigation';
import FileUpload from '@/components/FileUpload';

export default function Home() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="text-center mb-10 max-w-2xl">
        <h1 className="text-4xl font-bold text-gray-900 mb-4 tracking-tight">Pharmacogenomics AI Platform</h1>
        <p className="text-lg text-gray-600">
          Upload a raw genetic report (VCF, 23andMe, FASTA) to generate a clinical-grade pharmacogenomic analysis using our local, privacy-preserving LLM pipeline.
        </p>
      </div>

      <div className="w-full">
        <FileUpload onUploadSuccess={(jobId) => router.push(`/dashboard/${jobId}`)} />
      </div>
    </div>
  );
}