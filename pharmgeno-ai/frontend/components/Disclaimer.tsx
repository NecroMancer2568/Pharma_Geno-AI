'use client';

import { AlertTriangle } from 'lucide-react';

interface DisclaimerProps {
  prominent?: boolean;
}

export default function Disclaimer({ prominent = false }: DisclaimerProps) {
  if (prominent) {
    // Non-dismissible prominent disclaimer for report page (per requirements)
    return (
      <div className="p-6 rounded-xl bg-amber-500/20 border-2 border-amber-500/50">
        <div className="flex items-start gap-4">
          <AlertTriangle className="w-8 h-8 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <h2 className="text-lg font-bold text-amber-400 mb-2">
              Important Medical Disclaimer
            </h2>
            <p className="text-amber-200 text-sm leading-relaxed">
              <strong>This report is for educational purposes only and is NOT medical advice.</strong>
            </p>
            <ul className="mt-3 text-amber-200/80 text-sm space-y-1">
              <li>• Do NOT make medication changes without consulting your healthcare provider</li>
              <li>• This analysis is based on current research and may not reflect all drug interactions</li>
              <li>• Your healthcare provider has access to your complete medical history</li>
              <li>• Pharmacogenomic testing is one of many factors in medication decisions</li>
            </ul>
            <p className="mt-4 text-amber-200 text-sm font-medium">
              Always discuss these results with your doctor, pharmacist, or genetic counselor before making any changes to your medication regimen.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Standard disclaimer for other pages
  return (
    <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-slate-400">
          <strong className="text-slate-300">Medical Disclaimer:</strong> PharmGeno AI provides educational information based on pharmacogenomic research. 
          This is not medical advice. Always consult your healthcare provider before making medication decisions.
        </div>
      </div>
    </div>
  );
}
