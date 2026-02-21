'use client';

import { useEffect, useState } from 'react';
import { getViolations } from '@/lib/api';
import ViolationTable from '@/components/ViolationTable';

export default function ViolationsPage() {
  const [violations, setViolations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    severity: '',
    status: '',
  });

  const loadViolations = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (filters.severity) params.severity = filters.severity;
      if (filters.status) params.status = filters.status;
      
      const response = await getViolations(params);
      setViolations(response.data);
    } catch (error) {
      console.error('Failed to load violations:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadViolations();
  }, [filters]);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Violations</h1>
          <p className="mt-2 text-gray-600">Review and manage compliance violations</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Severity
              </label>
              <select
                value={filters.severity}
                onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Statuses</option>
                <option value="open">Open</option>
                <option value="in_review">In Review</option>
                <option value="resolved">Resolved</option>
                <option value="false_positive">False Positive</option>
              </select>
            </div>
          </div>
        </div>

        {/* Violations Table */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold">
              Violations ({violations.length})
            </h2>
          </div>
          
          {loading ? (
            <div className="p-6 text-center text-gray-500">Loading violations...</div>
          ) : violations.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              No violations found. Try adjusting your filters or run a scan from the dashboard.
            </div>
          ) : (
            <ViolationTable violations={violations} />
          )}
        </div>
      </div>
    </div>
  );
}
