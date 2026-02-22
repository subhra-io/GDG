'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface PredictionStats {
  total_predictions: number;
  risk_distribution: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  model_accuracy: number | null;
}

export default function PredictionWidget() {
  const [stats, setStats] = useState<PredictionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/predictions/statistics');
      
      if (!response.ok) {
        throw new Error('Failed to fetch prediction statistics');
      }
      
      const data = await response.json();
      setStats(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg shadow p-6 border border-purple-200">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg shadow p-6 border border-purple-200">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">🔮 Predictive Risk Analysis</h2>
            <p className="text-sm text-gray-600">ML-powered violation prediction</p>
          </div>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-yellow-800">
          {error}
        </div>
      </div>
    );
  }

  const totalHighRisk = (stats?.risk_distribution.high || 0) + (stats?.risk_distribution.critical || 0);

  return (
    <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg shadow p-6 border border-purple-200">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
          <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div>
          <h2 className="text-lg font-semibold text-gray-900">🔮 Predictive Risk Analysis</h2>
          <p className="text-sm text-gray-600">ML-powered violation prediction</p>
        </div>
      </div>

      {stats && stats.total_predictions > 0 ? (
        <>
          {/* High Risk Alert */}
          {totalHighRisk > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span className="font-semibold text-red-900">High Risk Records Detected</span>
              </div>
              <p className="text-2xl font-bold text-red-600">{totalHighRisk}</p>
              <p className="text-xs text-red-700 mt-1">Require immediate attention</p>
            </div>
          )}

          {/* Risk Distribution */}
          <div className="space-y-3 mb-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">🔴 Critical Risk</span>
              <span className="font-semibold text-red-600">{stats.risk_distribution.critical || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">🟠 High Risk</span>
              <span className="font-semibold text-orange-600">{stats.risk_distribution.high || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">🟡 Medium Risk</span>
              <span className="font-semibold text-yellow-600">{stats.risk_distribution.medium || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">🟢 Low Risk</span>
              <span className="font-semibold text-green-600">{stats.risk_distribution.low || 0}</span>
            </div>
          </div>

          {/* Model Accuracy */}
          {stats.model_accuracy !== null && (
            <div className="bg-white rounded-lg p-3 mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-gray-600">Model Accuracy</span>
                <span className="text-sm font-bold text-purple-600">{stats.model_accuracy.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-purple-600 h-2 rounded-full transition-all"
                  style={{ width: `${stats.model_accuracy}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Total Predictions */}
          <div className="text-center py-3 bg-white rounded-lg mb-4">
            <p className="text-2xl font-bold text-purple-600">{stats.total_predictions}</p>
            <p className="text-xs text-gray-600">Total Predictions Made</p>
          </div>
        </>
      ) : (
        <div className="text-center py-8">
          <svg className="w-16 h-16 text-purple-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <p className="text-sm text-gray-600 mb-2">No predictions yet</p>
          <p className="text-xs text-gray-500">Start analyzing records to see predictions</p>
        </div>
      )}

      {/* Action Button */}
      <Link 
        href="/predictions"
        className="block w-full text-center bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition-colors font-medium text-sm"
      >
        View All Predictions →
      </Link>
    </div>
  );
}
