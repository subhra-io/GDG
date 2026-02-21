interface RemediationStep {
  step_number: number;
  action: string;
  responsible_party: string;
  priority: string;
  estimated_time: string;
  prevents_recurrence: boolean;
}

interface RemediationStepsProps {
  steps: RemediationStep[];
}

export default function RemediationSteps({ steps }: RemediationStepsProps) {
  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'immediate': return 'bg-red-100 text-red-800 border-red-300';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  if (!steps || steps.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      {steps.map((step, index) => (
        <div 
          key={index}
          className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex items-start gap-4">
            {/* Step Number */}
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                {step.step_number}
              </div>
            </div>

            {/* Step Content */}
            <div className="flex-1">
              <div className="flex items-start justify-between gap-4 mb-2">
                <p className="text-gray-900 font-medium">{step.action}</p>
                <span className={`px-2 py-1 text-xs font-medium rounded border whitespace-nowrap ${getPriorityColor(step.priority)}`}>
                  {step.priority}
                </span>
              </div>

              <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <span>{step.responsible_party}</span>
                </div>

                <div className="flex items-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>{step.estimated_time}</span>
                </div>

                {step.prevents_recurrence && (
                  <div className="flex items-center gap-1 text-green-600">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="font-medium">Prevents recurrence</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
