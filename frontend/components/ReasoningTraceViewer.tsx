"use client";

import { useState, useEffect } from "react";

interface PolicyReference {
  clause: string;
  page: number;
  document_name: string;
}

interface ReasoningStep {
  step_number: number;
  description: string;
  rules_evaluated: string[];
  policy_references: PolicyReference[];
  confidence_score: number;
  outcome: "pass" | "fail" | "inconclusive";
}

interface ReasoningTrace {
  id: string;
  violation_id: string;
  steps: ReasoningStep[];
  created_at: string;
}

interface ReasoningTraceViewerProps {
  violationId: string;
}

export default function ReasoningTraceViewer({ violationId }: ReasoningTraceViewerProps) {
  const [trace, setTrace] = useState<ReasoningTrace | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchReasoningTrace();
  }, [violationId]);

  const fetchReasoningTrace = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/violations/${violationId}/reasoning-trace`
      );
      
      if (!response.ok) {
        if (response.status === 404) {
          setError("No reasoning trace available for this violation");
        } else {
          throw new Error("Failed to fetch reasoning trace");
        }
        return;
      }
      
      const data = await response.json();
      setTrace(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/violations/${violationId}/reasoning-trace/export`
      );
      
      if (!response.ok) throw new Error("Export failed");
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `reasoning_trace_${violationId}.txt`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert("Failed to export reasoning trace");
    }
  };

  const getOutcomeColor = (outcome: string) => {
    switch (outcome) {
      case "pass":
        return "text-green-600 bg-green-50";
      case "fail":
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 90) return "bg-green-500";
    if (score >= 70) return "bg-blue-500";
    if (score >= 50) return "bg-yellow-500";
    return "bg-red-500";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800">{error}</p>
      </div>
    );
  }

  if (!trace) {
    return null;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">AI Reasoning Trace</h3>
        <button
          onClick={handleExport}
          className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
        >
          Export as Text
        </button>
      </div>

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>

        {/* Steps */}
        <div className="space-y-6">
          {trace.steps.map((step, index) => (
            <div key={step.step_number} className="relative pl-16">
              {/* Step number circle */}
              <div className="absolute left-0 flex items-center justify-center w-16 h-16">
                <div className="flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 border-4 border-white shadow">
                  <span className="text-lg font-bold text-blue-600">{step.step_number}</span>
                </div>
              </div>

              {/* Step content */}
              <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="text-sm font-medium text-gray-900 flex-1">
                    {step.description}
                  </h4>
                  <span className={`ml-2 px-2 py-1 text-xs font-medium rounded ${getOutcomeColor(step.outcome)}`}>
                    {step.outcome}
                  </span>
                </div>

                {/* Confidence score */}
                <div className="mb-3">
                  <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                    <span>Confidence</span>
                    <span className="font-medium">{step.confidence_score}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${getConfidenceColor(step.confidence_score)}`}
                      style={{ width: `${step.confidence_score}%` }}
                    ></div>
                  </div>
                </div>

                {/* Rules evaluated */}
                {step.rules_evaluated && step.rules_evaluated.length > 0 && (
                  <div className="mb-2">
                    <p className="text-xs font-medium text-gray-700 mb-1">Rules Evaluated:</p>
                    <div className="flex flex-wrap gap-1">
                      {step.rules_evaluated.map((rule, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded"
                        >
                          {rule}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Policy references */}
                {step.policy_references && step.policy_references.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-gray-700 mb-1">Policy References:</p>
                    <div className="space-y-1">
                      {step.policy_references.map((ref, idx) => (
                        <div key={idx} className="text-xs text-gray-600 bg-gray-50 p-2 rounded">
                          <p className="font-medium">{ref.clause}</p>
                          <p className="text-gray-500">
                            {ref.document_name} - Page {ref.page}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="text-xs text-gray-500 text-center pt-4">
        Generated on {new Date(trace.created_at).toLocaleString()}
      </div>
    </div>
  );
}
