'use client';

import { motion } from 'framer-motion';
import { ChevronDown, AlertTriangle, CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import { useState } from 'react';
import RiskBadge from './RiskBadge';

interface DrugReport {
  name: string;
  compatibility: 'safe' | 'moderate_risk' | 'high_risk' | 'contraindicated';
  score: number;
  gene_variants_involved: string[];
  explanation: string;
  alternatives: string[];
  recommendation: string;
}

interface ReportCardProps {
  drug: DrugReport;
  index: number;
}

export default function ReportCard({ drug, index }: ReportCardProps) {
  const [isExpanded, setIsExpanded] = useState(drug.compatibility !== 'safe');

  const getIcon = () => {
    switch (drug.compatibility) {
      case 'safe':
        return <CheckCircle className="w-6 h-6 text-green-400" />;
      case 'moderate_risk':
        return <AlertCircle className="w-6 h-6 text-yellow-400" />;
      case 'high_risk':
        return <AlertTriangle className="w-6 h-6 text-orange-400" />;
      case 'contraindicated':
        return <XCircle className="w-6 h-6 text-red-400" />;
    }
  };

  const getBorderColor = () => {
    switch (drug.compatibility) {
      case 'safe':
        return 'border-green-500/30';
      case 'moderate_risk':
        return 'border-yellow-500/30';
      case 'high_risk':
        return 'border-orange-500/30';
      case 'contraindicated':
        return 'border-red-500/30';
    }
  };

  const getBgColor = () => {
    switch (drug.compatibility) {
      case 'safe':
        return 'bg-green-500/5';
      case 'moderate_risk':
        return 'bg-yellow-500/5';
      case 'high_risk':
        return 'bg-orange-500/5';
      case 'contraindicated':
        return 'bg-red-500/5';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 + index * 0.05 }}
      className={`rounded-xl border ${getBorderColor()} ${getBgColor()} overflow-hidden`}
    >
      {/* Header - Always visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center gap-4 hover:bg-white/5 transition-colors"
      >
        {getIcon()}
        
        <div className="flex-1 text-left">
          <h3 className="text-lg font-semibold">{drug.name}</h3>
          <p className="text-sm text-slate-400">{drug.explanation}</p>
        </div>

        <RiskBadge compatibility={drug.compatibility} score={drug.score} />
        
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown className="w-5 h-5 text-slate-400" />
        </motion.div>
      </button>

      {/* Expanded content */}
      <motion.div
        initial={false}
        animate={{ height: isExpanded ? 'auto' : 0, opacity: isExpanded ? 1 : 0 }}
        transition={{ duration: 0.3 }}
        className="overflow-hidden"
      >
        <div className="px-4 pb-4 space-y-4 border-t border-white/5 pt-4">
          {/* Gene variants */}
          {drug.gene_variants_involved.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-slate-400 mb-2">Gene Variants Involved</h4>
              <div className="flex flex-wrap gap-2">
                {drug.gene_variants_involved.map((variant) => (
                  <span
                    key={variant}
                    className="px-3 py-1 rounded-full text-sm bg-slate-700 text-cyan-400 font-mono"
                  >
                    {variant}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Recommendation */}
          <div>
            <h4 className="text-sm font-medium text-slate-400 mb-2">Recommendation</h4>
            <p className="text-slate-300">{drug.recommendation}</p>
          </div>

          {/* Alternatives */}
          {drug.alternatives.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-slate-400 mb-2">Potential Alternatives</h4>
              <div className="flex flex-wrap gap-2">
                {drug.alternatives.map((alt) => (
                  <span
                    key={alt}
                    className="px-3 py-1 rounded-full text-sm bg-slate-700 text-slate-300"
                  >
                    {alt}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
