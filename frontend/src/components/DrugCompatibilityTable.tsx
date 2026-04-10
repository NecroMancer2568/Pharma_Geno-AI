import { DrugCompatibility } from '@/lib/types';

export default function DrugCompatibilityTable({ compatibilities }: { compatibilities: DrugCompatibility[] }) {
  if (!compatibilities || compatibilities.length === 0) return null;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-5 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-800">Drug Compatibility Profile</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 text-gray-600 text-sm">
              <th className="px-6 py-3 font-medium">Drug</th>
              <th className="px-6 py-3 font-medium">Gene</th>
              <th className="px-6 py-3 font-medium">Risk Level</th>
              <th className="px-6 py-3 font-medium">Recommendation</th>
              <th className="px-6 py-3 font-medium">Evidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 text-sm">
            {compatibilities.map((item, idx) => (
              <tr key={idx} className="hover:bg-gray-50 transition">
                <td className="px-6 py-4 font-medium text-gray-800">{item.drug_name}</td>
                <td className="px-6 py-4 text-gray-600">{item.gene}</td>
                <td className="px-6 py-4">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                    item.risk_level === 'HIGH' ? 'bg-red-100 text-red-700' :
                    item.risk_level === 'MODERATE' ? 'bg-amber-100 text-amber-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {item.risk_level}
                  </span>
                </td>
                <td className="px-6 py-4 text-gray-600 max-w-md truncate" title={item.recommendation}>
                  {item.recommendation}
                </td>
                <td className="px-6 py-4 text-gray-500">
                  {item.evidence_level}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}