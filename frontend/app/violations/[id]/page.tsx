'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getViolation } from '@/lib/api';
import Link from 'next/link';
import RemediationSteps from '@/components/RemediationSteps';

export default function ViolationDetailPage() {
  const params = useParams();
  const [violation, setViolation] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadViolation = async () => {
      try {
        const response = await getViolation(params.id as string);
        setViolation(response.data);
      } catch (error) {
        console.error('Failed to load violation:', error);
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      loadViolation();
    }
  }, [params.id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl">Loading violation details...</div>
      </div>
    );
  }

  if (!violation) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl text-red-600">Violation not found</div>
      </div>
    );
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-300';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <Link href="/violations" className="text-blue-600 hover:text-blue-800">
            ← Back to Violations
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          {/* Header */}
          <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
            <div className="flex justify-between items-start">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Violation Details</h1>
                <p className="mt-1 text-sm text-gray-500">ID: {violation.id}</p>
              </div>
              <span className={`px-3 py-1 text-sm font-medium rounded-full border ${getSeverityColor(violation.severity)}`}>
                {violation.severity}
              </span>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Rule Information */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Rule Violated</h2>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-900">{violation.rule_description}</p>
              </div>
            </div>

            {/* AI Justification */}
            {violation.ai_justification && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-3">AI Analysis</h2>
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <p className="text-gray-800 whitespace-pre-wrap">{violation.ai_justification}</p>
                </div>
              </div>
            )}

            {/* Remediation Steps */}
            {violation.remediation_steps && violation.remediation_steps.length > 0 && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-3">
                  Recommended Remediation Steps
                </h2>
                <RemediationSteps steps={violation.remediation_steps} />
              </div>
            )}

            {/* Record Data */}
            {violation.record_data && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-3">Record Data</h2>
                <div className="bg-gray-50 rounded-lg p-4">
                  <pre className="text-sm text-gray-800 overflow-x-auto">
                    {JSON.stringify(violation.record_data, null, 2)}
                  </pre>
                </div>
              </div>
            )}

            {/* Metadata */}
            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className="mt-1 font-medium text-gray-900">{violation.status.replace('_', ' ')}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Detected At</p>
                <p className="mt-1 font-medium text-gray-900">
                  {new Date(violation.detected_at).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Risk Score</p>
                <p className="mt-1 font-medium text-gray-900">{violation.risk_score || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Record ID</p>
                <p className="mt-1 font-medium text-gray-900">{violation.record_id}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
