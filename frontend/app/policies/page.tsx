'use client';

import { useEffect, useState } from 'react';
import { getPolicies, uploadPolicy, extractRules, deletePolicy, updatePolicy } from '@/lib/api';
import PolicyTypeFilter from '@/components/PolicyTypeFilter';
import Link from 'next/link';

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [extractingRules, setExtractingRules] = useState<string | null>(null);
  const [editingPolicy, setEditingPolicy] = useState<string | null>(null);
  const [newFilename, setNewFilename] = useState('');

  const loadPolicies = async () => {
    setLoading(true);
    try {
      const response = await getPolicies();
      setPolicies(response.data);
    } catch (error) {
      console.error('Failed to load policies:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPolicies();
  }, []);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadMessage('Uploading policy...');

    try {
      const response = await uploadPolicy(file);
      setUploadMessage(`Policy uploaded successfully! ID: ${response.data.policy_id}`);
      await loadPolicies();
      
      // Reset file input
      event.target.value = '';
    } catch (error: any) {
      setUploadMessage(`Upload failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleExtractRules = async (policyId: string) => {
    setExtractingRules(policyId);
    try {
      const response = await extractRules(policyId);
      alert(`Extracted ${response.data.rules_extracted} rules successfully!`);
      await loadPolicies();
    } catch (error: any) {
      alert(`Rule extraction failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setExtractingRules(null);
    }
  };

  const handleDeletePolicy = async (policyId: string, filename: string) => {
    if (!confirm(`Are you sure you want to delete "${filename}"? This will also delete all associated rules.`)) {
      return;
    }

    try {
      await deletePolicy(policyId);
      alert('Policy deleted successfully!');
      await loadPolicies();
    } catch (error: any) {
      alert(`Delete failed: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleRenamePolicy = async (policyId: string) => {
    if (!newFilename.trim()) {
      alert('Please enter a new filename');
      return;
    }

    try {
      await updatePolicy(policyId, { filename: newFilename });
      alert('Policy renamed successfully!');
      setEditingPolicy(null);
      setNewFilename('');
      await loadPolicies();
    } catch (error: any) {
      alert(`Rename failed: ${error.response?.data?.detail || error.message}`);
    }
  };

  const filteredPolicies = selectedType
    ? policies.filter(p => p.policy_type?.toUpperCase() === selectedType)
    : policies;

  const getPolicyTypeIcon = (type: string) => {
    switch (type?.toUpperCase()) {
      case 'AML': return '💰';
      case 'GDPR': return '🔒';
      case 'SOX': return '📊';
      case 'HIPAA': return '🏥';
      case 'PCI-DSS': return '💳';
      default: return '📋';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Policy Management</h1>
          <p className="mt-2 text-gray-600">Upload and manage compliance policy documents</p>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Upload New Policy</h2>
          <div className="flex items-center gap-4">
            <label className="flex-1">
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                disabled={uploading}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100
                  disabled:opacity-50 disabled:cursor-not-allowed"
              />
            </label>
          </div>
          {uploadMessage && (
            <div className={`mt-4 p-3 rounded-md ${
              uploadMessage.includes('failed') 
                ? 'bg-red-50 text-red-800' 
                : 'bg-green-50 text-green-800'
            }`}>
              {uploadMessage}
            </div>
          )}
          <div className="mt-4 text-sm text-gray-600">
            <p className="font-medium mb-2">Supported Policy Types:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>💰 Anti-Money Laundering (AML)</li>
              <li>🔒 Data Privacy (GDPR)</li>
              <li>📊 Financial Controls (SOX)</li>
              <li>🏥 Healthcare (HIPAA)</li>
              <li>💳 Payment Card (PCI-DSS)</li>
            </ul>
          </div>
        </div>

        {/* Policy Type Filter */}
        <div className="mb-6">
          <PolicyTypeFilter selectedType={selectedType} onChange={setSelectedType} />
        </div>

        {/* Policies List */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold">
              Policies ({filteredPolicies.length})
            </h2>
          </div>

          {loading ? (
            <div className="p-6 text-center text-gray-500">Loading policies...</div>
          ) : filteredPolicies.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              {selectedType 
                ? `No ${selectedType} policies found. Try a different filter or upload a new policy.`
                : 'No policies found. Upload a policy document to get started.'
              }
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredPolicies.map((policy) => (
                <div key={policy.id} className="p-6 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-2xl">{getPolicyTypeIcon(policy.policy_type)}</span>
                        <div className="flex-1">
                          {editingPolicy === policy.id ? (
                            <div className="flex items-center gap-2">
                              <input
                                type="text"
                                value={newFilename}
                                onChange={(e) => setNewFilename(e.target.value)}
                                placeholder={policy.filename}
                                className="flex-1 px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                              />
                              <button
                                onClick={() => handleRenamePolicy(policy.id)}
                                className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
                              >
                                Save
                              </button>
                              <button
                                onClick={() => {
                                  setEditingPolicy(null);
                                  setNewFilename('');
                                }}
                                className="px-3 py-1 bg-gray-300 text-gray-700 text-sm rounded-md hover:bg-gray-400"
                              >
                                Cancel
                              </button>
                            </div>
                          ) : (
                            <>
                              <h3 className="text-lg font-semibold text-gray-900">
                                {policy.filename}
                              </h3>
                              <p className="text-sm text-gray-500">
                                Uploaded {new Date(policy.uploaded_at).toLocaleDateString()}
                              </p>
                            </>
                          )}
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-4 text-sm text-gray-600 mt-3">
                        <div className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          <span>{(policy.file_size / 1024).toFixed(1)} KB</span>
                        </div>

                        <div className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                          </svg>
                          <span>{policy.rules_count || 0} rules extracted</span>
                        </div>

                        {policy.policy_type && (
                          <div className="flex items-center gap-1">
                            <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                              {policy.policy_type}
                            </span>
                          </div>
                        )}

                        <div className="flex items-center gap-1">
                          <span className={`px-2 py-1 text-xs font-medium rounded ${
                            policy.status === 'processed' 
                              ? 'bg-green-100 text-green-800'
                              : policy.status === 'processing'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {policy.status}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-col gap-2 ml-4">
                      {policy.status === 'uploaded' && (
                        <button
                          onClick={() => handleExtractRules(policy.id)}
                          disabled={extractingRules === policy.id}
                          className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                        >
                          {extractingRules === policy.id ? 'Extracting...' : 'Extract Rules'}
                        </button>
                      )}
                      
                      <Link
                        href={`/policies/${policy.id}`}
                        className="px-4 py-2 bg-gray-100 text-gray-700 text-sm rounded-md hover:bg-gray-200 text-center"
                      >
                        View Details
                      </Link>

                      <button
                        onClick={() => {
                          setEditingPolicy(policy.id);
                          setNewFilename(policy.filename);
                        }}
                        className="px-4 py-2 bg-yellow-100 text-yellow-700 text-sm rounded-md hover:bg-yellow-200"
                      >
                        Rename
                      </button>

                      <button
                        onClick={() => handleDeletePolicy(policy.id, policy.filename)}
                        className="px-4 py-2 bg-red-100 text-red-700 text-sm rounded-md hover:bg-red-200"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
