'use client';

import { useEffect, useState } from 'react';
import { getDashboardMetrics, scanViolations } from '@/lib/api';
import MetricCard from '@/components/MetricCard';
import ComplianceGauge from '@/components/ComplianceGauge';

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [scanMessage, setScanMessage] = useState('');

  const loadMetrics = async () => {
    try {
      const response = await getDashboardMetrics();
      setMetrics(response.data);
    } catch (error) {
      console.error('Failed to load metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMetrics();
  }, []);

  const handleScan = async () => {
    setScanning(true);
    setScanMessage('Scanning for violations...');
    
    try {
      const response = await scanViolations();
      setScanMessage(`Scan complete! Found ${response.data.violations_detected} violations.`);
      // Reload metrics after scan
      await loadMetrics();
    } catch (error: any) {
      setScanMessage(`Scan failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setScanning(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Compliance Dashboard</h1>
          <p className="mt-2 text-gray-600">Monitor policy compliance and violations in real-time</p>
        </div>

        {/* Scan Button */}
        <div className="mb-6">
          <button
            onClick={handleScan}
            disabled={scanning}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
          >
            {scanning ? 'Scanning...' : 'Scan for Violations'}
          </button>
          {scanMessage && (
            <div className={`mt-2 p-3 rounded-md ${
              scanMessage.includes('failed') 
                ? 'bg-red-50 text-red-800' 
                : 'bg-green-50 text-green-800'
            }`}>
              {scanMessage}
            </div>
          )}
        </div>

        {/* Compliance Score */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <ComplianceGauge score={metrics?.compliance_score || 0} />
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <MetricCard
            title="Total Violations"
            value={metrics?.total_violations || 0}
            color="red"
          />
          <MetricCard
            title="Active Policies"
            value={metrics?.total_policies || 0}
            color="blue"
          />
          <MetricCard
            title="Active Rules"
            value={metrics?.total_rules || 0}
            color="green"
          />
          <MetricCard
            title="Records Monitored"
            value={metrics?.total_records || 0}
            color="yellow"
          />
        </div>

        {/* Severity Breakdown */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Violations by Severity</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-red-600">
                {metrics?.violations_by_severity?.critical || 0}
              </p>
              <p className="text-sm text-gray-600">Critical</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-orange-600">
                {metrics?.violations_by_severity?.high || 0}
              </p>
              <p className="text-sm text-gray-600">High</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-yellow-600">
                {metrics?.violations_by_severity?.medium || 0}
              </p>
              <p className="text-sm text-gray-600">Medium</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-600">
                {metrics?.violations_by_severity?.low || 0}
              </p>
              <p className="text-sm text-gray-600">Low</p>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Quick Stats</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Open Violations</span>
              <span className="font-semibold">{metrics?.violations_by_status?.open || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">In Review</span>
              <span className="font-semibold">{metrics?.violations_by_status?.in_review || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Resolved</span>
              <span className="font-semibold text-green-600">{metrics?.violations_by_status?.resolved || 0}</span>
            </div>
          </div>
        </div>

        {/* AI Features Showcase */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow p-6 border border-blue-200">
          <h2 className="text-xl font-semibold mb-4 text-gray-900">🤖 AI-Powered Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-gray-900">Rule Extraction</h3>
              </div>
              <p className="text-sm text-gray-600">
                Automatically extracts compliance rules from PDF policies using GPT-4 with structured validation
              </p>
            </div>

            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-gray-900">Smart Justifications</h3>
              </div>
              <p className="text-sm text-gray-600">
                Generates business-friendly explanations for violations with quality validation
              </p>
            </div>

            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-gray-900">Remediation Steps</h3>
              </div>
              <p className="text-sm text-gray-600">
                Provides actionable remediation steps with priorities, responsible parties, and time estimates
              </p>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-blue-200">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Supported Policy Types:</span>
              <div className="flex gap-2">
                <span className="px-2 py-1 bg-white rounded text-xs font-medium">💰 AML</span>
                <span className="px-2 py-1 bg-white rounded text-xs font-medium">🔒 GDPR</span>
                <span className="px-2 py-1 bg-white rounded text-xs font-medium">📊 SOX</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
