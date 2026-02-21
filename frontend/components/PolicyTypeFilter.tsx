interface PolicyTypeFilterProps {
  selectedType: string;
  onChange: (type: string) => void;
}

export default function PolicyTypeFilter({ selectedType, onChange }: PolicyTypeFilterProps) {
  const policyTypes = [
    { value: '', label: 'All Policy Types', icon: '📋' },
    { value: 'AML', label: 'Anti-Money Laundering', icon: '💰' },
    { value: 'GDPR', label: 'Data Privacy (GDPR)', icon: '🔒' },
    { value: 'SOX', label: 'Financial Controls (SOX)', icon: '📊' },
    { value: 'HIPAA', label: 'Healthcare (HIPAA)', icon: '🏥' },
    { value: 'PCI-DSS', label: 'Payment Card (PCI-DSS)', icon: '💳' },
  ];

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <label className="block text-sm font-medium text-gray-700 mb-3">
        Policy Type
      </label>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
        {policyTypes.map((type) => (
          <button
            key={type.value}
            onClick={() => onChange(type.value)}
            className={`
              flex flex-col items-center justify-center p-3 rounded-lg border-2 transition-all
              ${selectedType === type.value
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-200 hover:border-gray-300 text-gray-700'
              }
            `}
          >
            <span className="text-2xl mb-1">{type.icon}</span>
            <span className="text-xs font-medium text-center">{type.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
