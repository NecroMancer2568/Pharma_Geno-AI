import { Download } from 'lucide-react';
import { api } from '@/lib/api';

export default function ReportExport({ jobId }: { jobId: string }) {
  return (
    <button
      onClick={() => api.downloadPdf(jobId)}
      className="flex items-center gap-2 bg-gray-900 hover:bg-gray-800 text-white px-4 py-2 rounded-lg font-medium transition shadow-sm"
    >
      <Download className="w-4 h-4" />
      Export Clinical PDF
    </button>
  );
}