'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getPolicy, getPolicyRules, extractRules, deletePolicy } from '@/lib/api';
import Link from 'next/link';

export default function PolicyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const policyId = params.id as string;

  const [policy, setPolicy] = useState<any>(null);
  const [rules, setRules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [extracting, setExtracting] = useState(false);

  const loadPolicy = async () => {
    try {
      const [policyRes, rulesRes] = await Promise.all([
        getPolicy(policyId),
        getPolicyRules(policyId)
      ]);
      setPolicy(policyRes.data);
      setRules(rulesRes.data);
    } catch (error) {
      console.error('Failed to load policy:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (policyId) {
      loadPolicy();
    }
  }, [policyId]);

  const handleExtractRules = async () => {
    setExtracting(true);
    try {
      const response = await extractRules(policyId);
      alert(`Extracted ${response.data.rules_extracted} rules successfully!`);
      await loadPolicy();
    } catch (error: any) {
      alert(`Rule extraction failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setExtracting(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to delete "${policy?.filename}"?`)) {
      return;
    }

    try {
      await deletePolicy(policyId);
      alert('Policy deleted successfully!');
      router.push('/policies');
    } catch (error: any) {
      alert(`Delete failed: ${error.response?.data?.detail || error.message}`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading policy...</div>
      </div>
    );
  }

  if (!policy) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Policy Not Found</h2>
          <Link href="/policies" className="text-blue-600 hover:text-blue-800">
            Back to Policies
          </Link>
        </div>
      </div>
    );
  }

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6">
          <Link href="/policies" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
            ← Back to Policies
          </Link>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{policy.filename}</h1>
              <p className="mt-2 text-gray-600">
                Uploaded {new Date(policy.uploaded_at || policy.upload_timestamp).toLocaleString()}
              </p>
            </div>
            <div className="flex gap-2">
              {policy.status === 'uploaded' && (
                <button
                  onClick={handleExtractRules}
                  disabled={extracting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {extracting ? 'Extracting...' : 'Extract Rules'}
                </button>
              )}
              <button
                onClick={handleDelete}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Delete Policy
              </button>
            </div>
          </div>
        </div>

        {/* Policy Info */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Policy Information</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">File Size</p>
              <p className="text-lg font-semibold">
                {((policy.file_size || policy.file_size_bytes) / 1024).toFixed(1)} KB
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <p className="text-lg font-semibold">
                <span className={`px-2 py-1 text-sm rounded ${
                  policy.status === 'processed' 
                    ? 'bg-green-100 text-green-800'
                    : policy.status === 'processing'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {policy.status}
                </span>
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Policy Type</p>
              <p className="text-lg font-semibold">
                {policy.policy_type || 'Not specified'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Rules Extracted</p>
              <p className="text-lg font-semibold">{rules.length}</p>
            </div>
          </div>
        </div>

        {/* Extracted Text Preview */}
        {policy.extracted_text && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Extracted Text Preview</h2>
            <div className="bg-gray-50 p-4 rounded-md max-h-64 overflow-y-auto">
              <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                {policy.extracted_text.substring(0, 1000)}
                {policy.extracted_text.length > 1000 && '...'}
              </pre>
            </div>
          </div>
        )}

        {/* Rules */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold">
              Compliance Rules ({rules.length})
            </h2>
          </div>

          {rules.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              {policy.status === 'uploaded' ? (
                <>
                  <p className="mb-4">No rules extracted yet.</p>
                  <button
                    onClick={handleExtractRules}
                    disabled={extracting}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    {extracting ? 'Extracting...' : 'Extract Rules Now'}
                  </button>
                </>
              ) : (
                <p>No rules found for this policy.</p>
              )}
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {rules.map((rule, index) => (
                <div key={rule.id} className="p-6 hover:bg-gray-50">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <span className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-800 rounded-full font-semibold">
                        {index + 1}
                      </span>
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {rule.description || 'Compliance Rule'}
                        </h3>
                        {rule.page_number && (
                          <p className="text-sm text-gray-500">Page {rule.page_number}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-3 py-1 text-sm font-medium rounded ${getSeverityColor(rule.severity)}`}>
                        {rule.severity}
                      </span>
                      {rule.is_active ? (
                        <span className="px-3 py-1 text-sm font-medium bg-green-100 text-green-800 rounded">
                          Active
                        </span>
                      ) : (
                        <span className="px-3 py-1 text-sm font-medium bg-gray-100 text-gray-800 rounded">
                          Inactive
                        </span>
                      )}
                    </div>
                  </div>

                  {rule.validation_logic && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-md">
                      <p className="text-sm font-medium text-gray-700 mb-2">Validation Logic:</p>
                      <pre className="text-xs text-gray-600 overflow-x-auto">
                        {JSON.stringify(rule.validation_logic, null, 2)}
                      </pre>
                    </div>
                  )}

                  {rule.confidence_score && (
                    <div className="mt-2 text-sm text-gray-600">
                      Confidence: {(parseFloat(rule.confidence_score) * 100).toFixed(0)}%
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
