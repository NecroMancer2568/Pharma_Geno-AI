import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

export default function RiskGauge({ score }: { score: number }) {
  const data = [
    { name: 'Score', value: score },
    { name: 'Remaining', value: 100 - score },
  ];

  let color = '#22c55e'; // Green
  let label = 'Low Risk';
  
  if (score > 33) {
    color = '#f59e0b'; // Amber
    label = 'Moderate Risk';
  }
  if (score > 66) {
    color = '#ef4444'; // Red
    label = 'High Risk';
  }

  const COLORS = [color, '#e5e7eb'];

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center justify-center">
      <h3 className="text-lg font-semibold text-gray-700 mb-4">Overall Genomic Risk</h3>
      <div className="w-48 h-48 relative">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              startAngle={180}
              endAngle={0}
              innerRadius={60}
              outerRadius={80}
              paddingAngle={0}
              dataKey="value"
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center mt-12">
          <span className="text-4xl font-bold text-gray-800">{Math.round(score)}</span>
          <span className={`text-sm font-semibold mt-1 px-2 py-0.5 rounded ${
            score > 66 ? 'bg-red-100 text-red-700' : score > 33 ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'
          }`}>
            {label}
          </span>
        </div>
      </div>
    </div>
  );
}