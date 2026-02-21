'use client';

import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

interface ComplianceGaugeProps {
  score: number;
}

export default function ComplianceGauge({ score }: ComplianceGaugeProps) {
  const data = [
    { name: 'Score', value: score },
    { name: 'Remaining', value: 100 - score },
  ];

  const getColor = (score: number) => {
    if (score >= 80) return '#10b981'; // green
    if (score >= 60) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  const color = getColor(score);

  return (
    <div className="flex flex-col items-center">
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            startAngle={180}
            endAngle={0}
            innerRadius={60}
            outerRadius={80}
            dataKey="value"
          >
            <Cell fill={color} />
            <Cell fill="#e5e7eb" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-4 text-center">
        <p className="text-4xl font-bold" style={{ color }}>{score}</p>
        <p className="text-sm text-gray-600">Compliance Score</p>
      </div>
    </div>
  );
}
