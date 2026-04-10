import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File } from 'lucide-react';
import { api } from '@/lib/api';

export default function FileUpload({ onUploadSuccess }: { onUploadSuccess: (jobId: string) => void }) {
  const [patientId, setPatientId] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError('');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: {
      'text/plain': ['.txt', '.tsv', '.vcf', '.fasta'],
      'application/gzip': ['.vcf.gz']
    },
    maxFiles: 1
  });

  const handleUpload = async () => {
    if (!patientId.trim()) {
      setError('Patient ID is required');
      return;
    }
    if (!file) {
      setError('Please select a file');
      return;
    }

    setIsUploading(true);
    setError('');

    try {
      const res = await api.uploadFile(file, patientId);
      onUploadSuccess(res.job_id);
    } catch (err: any) {
      setError(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto bg-white p-8 rounded-xl shadow-sm border border-gray-100">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800">Upload Genetic Report</h2>
      
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Patient ID / MRN</label>
        <input 
          type="text" 
          value={patientId}
          onChange={(e) => setPatientId(e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
          placeholder="Enter anonymized patient ID..."
        />
      </div>

      <div 
        {...getRootProps()} 
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition ${
          isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400 bg-gray-50'
        }`}
      >
        <input {...getInputProps()} />
        {file ? (
          <div className="flex flex-col items-center">
            <File className="w-12 h-12 text-blue-500 mb-3" />
            <p className="text-gray-700 font-medium">{file.name}</p>
            <p className="text-gray-500 text-sm mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <Upload className="w-12 h-12 text-gray-400 mb-3" />
            <p className="text-gray-600 font-medium">Drag & drop your file here</p>
            <p className="text-gray-400 text-sm mt-2">Supports .vcf, .vcf.gz, .txt, .tsv, .fasta</p>
          </div>
        )}
      </div>

      {error && <p className="text-red-500 text-sm mt-4 text-center">{error}</p>}

      <button
        onClick={handleUpload}
        disabled={isUploading || !file || !patientId}
        className="w-full mt-8 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {isUploading ? 'Uploading...' : 'Start Analysis'}
      </button>
    </div>
  );
}