'use client';

interface RiskBadgeProps {
  compatibility: 'safe' | 'moderate_risk' | 'high_risk' | 'contraindicated';
  score: number;
}

export default function RiskBadge({ compatibility, score }: RiskBadgeProps) {
  const getConfig = () => {
    switch (compatibility) {
      case 'safe':
        return {
          bg: 'bg-green-500/20',
          text: 'text-green-400',
          border: 'border-green-500/30',
          label: 'Safe'
        };
      case 'moderate_risk':
        return {
          bg: 'bg-yellow-500/20',
          text: 'text-yellow-400',
          border: 'border-yellow-500/30',
          label: 'Moderate Risk'
        };
      case 'high_risk':
        return {
          bg: 'bg-orange-500/20',
          text: 'text-orange-400',
          border: 'border-orange-500/30',
          label: 'High Risk'
        };
      case 'contraindicated':
        return {
          bg: 'bg-red-500/20',
          text: 'text-red-400',
          border: 'border-red-500/30',
          label: 'Contraindicated'
        };
    }
  };

  const config = getConfig();

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${config.bg} border ${config.border}`}>
      <span className={`text-sm font-medium ${config.text}`}>
        {config.label}
      </span>
      <span className={`text-xs ${config.text} opacity-75`}>
        {score}/10
      </span>
    </div>
  );
}
