'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Metrics {
  total_corrections: number;
  accuracy: number;
  false_positive_rate: number;
  true_positive_rate: number;
  needs_review_rate: number;
  avg_confidence: number;
}

interface RuleMetric {
  rule_id: string;
  rule_name: string;
  total_reviews: number;
  accuracy: number;
  false_positive_rate: number;
  true_positive_count: number;
  false_positive_count: number;
  needs_review_count: number;
  avg_confidence: number;
  trend: string;
  high_fp_rate: boolean;
}

interface Suggestion {
  rule_id: string;
  rule_name: string;
  issue: string;
  suggestion: string;
  priority: string;
}

export default function FeedbackPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [ruleMetrics, setRuleMetrics] = useState<RuleMetric[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch all data in parallel
      const [metricsRes, rulesRes, suggestionsRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/feedback/metrics'),
        fetch('http://localhost:8000/api/v1/feedback/rules'),
        fetch('http://localhost:8000/api/v1/feedback/suggestions')
      ]);
      
      if (!metricsRes.ok || !rulesRes.ok || !suggestionsRes.ok) {
        throw new Error('Failed to fetch feedback data');
      }
      
      const metricsData = await metricsRes.json();
      const rulesData = await rulesRes.json();
      const suggestionsData = await suggestionsRes.json();
      
      setMetrics(metricsData);
      setRuleMetrics(rulesData.rules || []);
      setSuggestions(suggestionsData.suggestions || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return '📈';
      case 'declining': return '📉';
      case 'stable': return '➡️';
      case 'insufficient_data': return '❓';
      default: return '➡️';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-50 border-red-300 text-red-800';
      case 'medium': return 'bg-yellow-50 border-yellow-300 text-yellow-800';
      case 'low': return 'bg-blue-50 border-blue-300 text-blue-800';
      default: return 'bg-gray-50 border-gray-300 text-gray-800';
    }
  };

  if (loading && !metrics) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading feedback data...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h1 className="text-3xl font-bold text-gray-900">Feedback & Learning</h1>
          </div>
          <p className="text-gray-600">AI accuracy metrics and improvement insights</p>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Overall Metrics */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">Overall Accuracy</p>
              <p className="text-3xl font-bold text-green-600">{metrics.accuracy.toFixed(1)}%</p>
              <p className="text-xs text-gray-500 mt-1">{metrics.total_corrections} corrections</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">True Positives</p>
              <p className="text-3xl font-bold text-blue-600">{metrics.true_positive_rate.toFixed(1)}%</p>
              <p className="text-xs text-gray-500 mt-1">AI was correct</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">False Positives</p>
              <p className="text-3xl font-bold text-orange-600">{metrics.false_positive_rate.toFixed(1)}%</p>
              <p className="text-xs text-gray-500 mt-1">AI was wrong</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">Avg Confidence</p>
              <p className="text-3xl font-bold text-purple-600">{(metrics.avg_confidence * 100).toFixed(1)}%</p>
              <p className="text-xs text-gray-500 mt-1">AI confidence score</p>
            </div>
          </div>
        )}

        {/* Improvement Suggestions */}
        {suggestions.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">🎯 Improvement Suggestions</h2>
            <div className="space-y-3">
              {suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className={`border rounded-lg p-4 ${getPriorityColor(suggestion.priority)}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold">{suggestion.rule_name}</span>
                        <span className="text-xs px-2 py-0.5 bg-white rounded-full">
                          {suggestion.priority.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm mb-2">
                        <span className="font-medium">Issue:</span> {suggestion.issue}
                      </p>
                      <p className="text-sm">
                        <span className="font-medium">Suggestion:</span> {suggestion.suggestion}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Rule Metrics Table */}
        {ruleMetrics.length > 0 ? (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">📊 Rule Performance</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Rule Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Reviews
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Accuracy
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      FP Rate
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Confidence
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Trend
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {ruleMetrics.map((rule) => (
                    <tr key={rule.rule_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className="text-sm font-medium text-gray-900">{rule.rule_name}</span>
                          {rule.high_fp_rate && (
                            <span className="ml-2 text-xs px-2 py-0.5 bg-red-100 text-red-800 rounded-full">
                              High FP
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {rule.total_reviews}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-sm font-medium ${
                          rule.accuracy >= 80 ? 'text-green-600' :
                          rule.accuracy >= 60 ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {rule.accuracy.toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-sm ${
                          rule.false_positive_rate > 30 ? 'text-red-600 font-medium' :
                          rule.false_positive_rate > 15 ? 'text-yellow-600' :
                          'text-gray-900'
                        }`}>
                          {rule.false_positive_rate.toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {(rule.avg_confidence * 100).toFixed(0)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className="flex items-center gap-1">
                          <span>{getTrendIcon(rule.trend)}</span>
                          <span className="text-gray-600 capitalize">{rule.trend.replace('_', ' ')}</span>
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <svg className="w-20 h-20 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Feedback Data Yet</h3>
            <p className="text-gray-600 mb-4">Start reviewing violations to see AI performance metrics</p>
            <Link
              href="/reviews"
              className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Go to Review Queue →
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
