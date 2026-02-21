"use client";

import { useState, useEffect } from "react";
import ClauseViewer from "./ClauseViewer";
import { jsPDF } from "jspdf";

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
  policyId?: string;
}

export default function ReasoningTraceViewer({ violationId, policyId }: ReasoningTraceViewerProps) {
  const [trace, setTrace] = useState<ReasoningTrace | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedClause, setSelectedClause] = useState<{
    policyId: string;
    pageNumber: number;
    clauseText: string;
  } | null>(null);

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

  const exportToPdf = () => {
    if (!trace) return;

    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 20;
    const maxWidth = pageWidth - 2 * margin;
    let yPos = 20;

    // Title
    doc.setFontSize(16);
    doc.setFont("helvetica", "bold");
    doc.text("AI Reasoning Trace Report", margin, yPos);
    yPos += 10;

    // Metadata
    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    doc.text(`Violation ID: ${violationId}`, margin, yPos);
    yPos += 6;
    doc.text(`Generated: ${new Date(trace.created_at).toLocaleString()}`, margin, yPos);
    yPos += 15;

    // Steps
    trace.steps.forEach((step, index) => {
      // Check if we need a new page
      if (yPos > 250) {
        doc.addPage();
        yPos = 20;
      }

      // Step header
      doc.setFontSize(12);
      doc.setFont("helvetica", "bold");
      doc.text(`Step ${step.step_number}: ${step.outcome.toUpperCase()}`, margin, yPos);
      yPos += 7;

      // Description
      doc.setFontSize(10);
      doc.setFont("helvetica", "normal");
      const descLines = doc.splitTextToSize(step.description, maxWidth);
      doc.text(descLines, margin, yPos);
      yPos += descLines.length * 5 + 3;

      // Confidence
      doc.text(`Confidence: ${step.confidence_score}%`, margin, yPos);
      yPos += 7;

      // Policy references
      if (step.policy_references && step.policy_references.length > 0) {
        doc.setFont("helvetica", "bold");
        doc.text("Policy References:", margin, yPos);
        yPos += 5;
        doc.setFont("helvetica", "normal");

        step.policy_references.forEach((ref) => {
          if (yPos > 270) {
            doc.addPage();
            yPos = 20;
          }
          const refText = `• "${ref.clause}" (${ref.document_name}, Page ${ref.page})`;
          const refLines = doc.splitTextToSize(refText, maxWidth - 5);
          doc.text(refLines, margin + 5, yPos);
          yPos += refLines.length * 5;
        });
      }

      yPos += 10;
    });

    // Save
    doc.save(`reasoning-trace-${violationId}.pdf`);
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
        <div className="flex gap-2">
          <button
            onClick={handleExport}
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Export as Text
          </button>
          <button
            onClick={exportToPdf}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            Export as PDF
          </button>
        </div>
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
                    <p className="text-xs font-medium text-gray-700 mb-1">📄 Policy References:</p>
                    <div className="space-y-1">
                      {step.policy_references.map((ref, idx) => (
                        <div key={idx} className="text-xs bg-blue-50 border border-blue-200 p-2 rounded">
                          <p className="font-medium text-blue-900 mb-1">"{ref.clause}"</p>
                          <div className="flex items-center justify-between">
                            <p className="text-blue-700">
                              {ref.document_name} - Page {ref.page}
                            </p>
                            {policyId && (
                              <button
                                onClick={() => setSelectedClause({
                                  policyId,
                                  pageNumber: ref.page,
                                  clauseText: ref.clause
                                })}
                                className="text-xs text-blue-600 hover:text-blue-800 underline font-medium"
                              >
                                View in Document →
                              </button>
                            )}
                          </div>
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

      {/* Clause Viewer Modal */}
      {selectedClause && (
        <ClauseViewer
          policyId={selectedClause.policyId}
          pageNumber={selectedClause.pageNumber}
          clauseText={selectedClause.clauseText}
          onClose={() => setSelectedClause(null)}
        />
      )}
    </div>
  );
}
