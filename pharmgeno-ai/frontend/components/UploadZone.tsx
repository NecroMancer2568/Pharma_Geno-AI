'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { Upload, FileText, AlertCircle } from 'lucide-react';

interface UploadZoneProps {
  onFileUpload: (file: File) => void;
}

export default function UploadZone({ onFileUpload }: UploadZoneProps) {
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setError(null);
    
    if (rejectedFiles.length > 0) {
      setError('Please upload a valid DNA data file (.txt)');
      return;
    }

    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      
      // Validate file size (max 50MB)
      if (file.size > 50 * 1024 * 1024) {
        setError('File size must be less than 50MB');
        return;
      }

      // Basic validation of file content
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        const lines = content.split('\n').slice(0, 10);
        
        // Check if it looks like a DNA file (has rs IDs or comment headers)
        const hasValidContent = lines.some(line => 
          line.startsWith('#') || 
          line.toLowerCase().startsWith('rs') ||
          /^rs\d+/i.test(line)
        );

        if (!hasValidContent) {
          setError('This does not appear to be a valid 23andMe or AncestryDNA file');
          return;
        }

        onFileUpload(file);
      };
      reader.readAsText(file.slice(0, 10000)); // Only read first 10KB for validation
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'text/csv': ['.csv'],
    },
    maxFiles: 1,
  });

  return (
    <div>
      <motion.div
        {...getRootProps()}
        className={`
          relative p-12 rounded-2xl border-2 border-dashed cursor-pointer
          transition-all duration-300 text-center
          ${isDragActive 
            ? 'border-cyan-400 bg-cyan-500/10' 
            : 'border-slate-600 hover:border-slate-500 hover:bg-slate-800/50'
          }
        `}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <input {...getInputProps()} />
        
        <motion.div
          className={`inline-flex p-4 rounded-full mb-6 ${
            isDragActive ? 'bg-cyan-500/20' : 'bg-slate-700'
          }`}
          animate={isDragActive ? { scale: [1, 1.1, 1] } : {}}
          transition={{ duration: 0.3 }}
        >
          {isDragActive ? (
            <FileText className="w-10 h-10 text-cyan-400" />
          ) : (
            <Upload className="w-10 h-10 text-slate-400" />
          )}
        </motion.div>

        <h3 className="text-xl font-semibold mb-2">
          {isDragActive ? 'Drop your file here' : 'Upload DNA Data File'}
        </h3>
        
        <p className="text-slate-400 mb-4">
          Drag and drop your 23andMe or AncestryDNA file, or click to browse
        </p>

        <p className="text-sm text-slate-500">
          Supported formats: .txt, .csv • Max size: 50MB
        </p>
      </motion.div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center gap-3"
        >
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <span className="text-red-400">{error}</span>
        </motion.div>
      )}

      <div className="mt-6 p-4 rounded-xl bg-slate-800/50 border border-slate-700">
        <h4 className="font-medium mb-2 flex items-center gap-2">
          <FileText className="w-4 h-4 text-cyan-400" />
          How to get your DNA file
        </h4>
        <ul className="text-sm text-slate-400 space-y-1">
          <li>• <strong>23andMe:</strong> Go to Settings → Download Raw Data</li>
          <li>• <strong>AncestryDNA:</strong> Go to DNA Settings → Download Raw DNA Data</li>
          <li>• Your file should be a .txt or .csv file with genetic variant data</li>
        </ul>
      </div>
    </div>
  );
}
