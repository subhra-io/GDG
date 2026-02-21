interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
  color?: 'blue' | 'green' | 'red' | 'yellow';
}

export default function MetricCard({ 
  title, 
  value, 
  subtitle, 
  trend,
  color = 'blue' 
}: MetricCardProps) {
  const colorClasses = {
    blue: 'border-blue-500 bg-blue-50',
    green: 'border-green-500 bg-green-50',
    red: 'border-red-500 bg-red-50',
    yellow: 'border-yellow-500 bg-yellow-50',
  };

  return (
    <div className={`rounded-lg border-l-4 ${colorClasses[color]} p-6 shadow-sm`}>
      <h3 className="text-sm font-medium text-gray-600">{title}</h3>
      <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
      {subtitle && (
        <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
      )}
      {trend && (
        <div className="mt-2">
          {trend === 'up' && <span className="text-sm text-red-600">↑ Increasing</span>}
          {trend === 'down' && <span className="text-sm text-green-600">↓ Decreasing</span>}
          {trend === 'neutral' && <span className="text-sm text-gray-600">→ Stable</span>}
        </div>
      )}
    </div>
  );
}
