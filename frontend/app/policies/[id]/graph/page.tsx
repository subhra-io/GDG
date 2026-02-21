'use client';

import { use } from 'react';
import { useRouter } from 'next/navigation';
import RuleGraphViewer from '@/components/RuleGraphViewer';

export default function RuleGraphPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const { id } = use(params);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="text-blue-600 hover:text-blue-800 mb-4 flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Policy
          </button>
          
          <h1 className="text-3xl font-bold text-gray-900">Rule Graph Visualization</h1>
          <p className="mt-2 text-gray-600">
            Interactive visualization of rule relationships and dependencies
          </p>
        </div>

        {/* Graph Viewer */}
        <RuleGraphViewer policyId={id} />

        {/* Additional Actions */}
        <div className="mt-6 flex gap-4">
          <button
            onClick={() => router.push(`/policies/${id}`)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            View Policy Details
          </button>
          <button
            onClick={() => window.location.href = `http://localhost:8000/api/v1/rules/conflicts/${id}`}
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
          >
            Check for Conflicts
          </button>
          <button
            onClick={() => window.location.href = `http://localhost:8000/api/v1/rules/cycles/${id}`}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Detect Circular Dependencies
          </button>
        </div>
      </div>
    </div>
  );
}
