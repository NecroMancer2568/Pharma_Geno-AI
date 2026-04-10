import { DiseaseRisk } from '@/lib/types';

export default function DiseaseRiskPanel({ risks }: { risks: DiseaseRisk[] }) {
  if (!risks || risks.length === 0) return null;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-5 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-800">Disease Predisposition Risks</h3>
      </div>
      <div className="p-6 grid gap-6">
        {risks.map((item, idx) => (
          <div key={idx} className="border-b border-gray-50 pb-6 last:border-0 last:pb-0">
            <div className="flex justify-between items-center mb-3">
              <div>
                <h4 className="font-semibold text-gray-800">{item.disease_name}</h4>
                <p className="text-xs text-gray-500 mt-1">Associated Genes: {item.associated_genes.join(', ')}</p>
              </div>
              <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                item.risk_category === 'HIGH' ? 'bg-red-100 text-red-700' :
                item.risk_category === 'MODERATE' ? 'bg-amber-100 text-amber-700' :
                'bg-green-100 text-green-700'
              }`}>
                {item.risk_category}
              </span>
            </div>
            
            <div className="mt-4">
              <div className="flex justify-between text-sm mb-1 text-gray-600">
                <span>Patient Risk ({item.risk_percentage}%)</span>
                <span>Pop. Average ({item.population_average}%)</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5 relative">
                {/* Population average marker */}
                <div 
                  className="absolute top-0 bottom-0 w-0.5 bg-gray-600 z-10"
                  style={{ left: `${item.population_average}%` }}
                />
                {/* Patient risk bar */}
                <div 
                  className={`h-2.5 rounded-full ${item.risk_category === 'HIGH' ? 'bg-red-500' : item.risk_category === 'MODERATE' ? 'bg-amber-500' : 'bg-green-500'}`} 
                  style={{ width: `${item.risk_percentage}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}