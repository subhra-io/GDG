'use client';

import { useEffect, useState } from 'react';

interface Prediction {
  id: string;
  record_id: string;
  violation_probability: number;
  confidence_score: number;
  risk_level: string;
  risk_factors: string[];
  recommendations: string[];
  predicted_at: string;
}

interface WhatIfScenario {
  record: Record<string, any>;
  changes: Record<string, any>;
}

export default function PredictionsPage() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPrediction, setSelectedPrediction] = useState<Prediction | null>(null);
  
  // What-if simulator state
  const [showWhatIf, setShowWhatIf] = useState(false);
  const [whatIfResult, setWhatIfResult] = useState<any>(null);
  const [whatIfLoading, setWhatIfLoading] = useState(false);

  useEffect(() => {
    fetchPredictions();
  }, []);

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/predictions/high-risk-records?threshold=0.4&limit=100');
      
      if (!response.ok) {
        throw new Error('Failed to fetch predictions');
      }
      
      const data = await response.json();
      setPredictions(data.high_risk_records || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const runWhatIfSimulation = async () => {
    try {
      setWhatIfLoading(true);
      
      const scenario: WhatIfScenario = {
        record: {
          transaction_id: 'TXN-WHATIF-001',
          amount: 50000,
          approver_1: null,
          approver_2: null,
          initiator: 'EMP001',
          customer_id: 'CUST001'
        },
        changes: {
          approver_1: 'EMP002',
          approver_2: 'EMP003'
        }
      };
      
      const response = await fetch('http://localhost:8000/api/v1/predictions/what-if', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scenario)
      });
      
      if (!response.ok) {
        throw new Error('What-if simulation failed');
      }
      
      const data = await response.json();
      setWhatIfResult(data);
    } catch (err) {
      alert('What-if simulation failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setWhatIfLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical': return '🔴';
      case 'high': return '🟠';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '⚪';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading predictions...</p>
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
            <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h1 className="text-3xl font-bold text-gray-900">Predictive Risk Analysis</h1>
          </div>
          <p className="text-gray-600">ML-powered violation prediction and what-if scenario analysis</p>
        </div>

        {/* Actions */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={fetchPredictions}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
          >
            🔄 Refresh Predictions
          </button>
          <button
            onClick={() => setShowWhatIf(!showWhatIf)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
          >
            🎯 What-If Simulator
          </button>
        </div>

        {/* What-If Simulator */}
        {showWhatIf && (
          <div className="bg-white rounded-lg shadow p-6 mb-6 border border-indigo-200">
            <h2 className="text-xl font-semibold mb-4 text-gray-900">What-If Scenario Simulator</h2>
            <p className="text-sm text-gray-600 mb-4">
              Simulate how changes to a record affect violation probability
            </p>
            
            <button
              onClick={runWhatIfSimulation}
              disabled={whatIfLoading}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium disabled:bg-gray-400"
            >
              {whatIfLoading ? 'Running Simulation...' : 'Run Sample Simulation'}
            </button>

            {whatIfResult && (
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Original */}
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <h3 className="font-semibold text-red-900 mb-2">Original Scenario</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-red-700">Risk Level:</span>
                      <span className="font-semibold text-red-900">{whatIfResult.original.risk_level}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-red-700">Probability:</span>
                      <span className="font-semibold text-red-900">
                        {(whatIfResult.original.violation_probability * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Modified */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h3 className="font-semibold text-green-900 mb-2">After Changes</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-green-700">Risk Level:</span>
                      <span className="font-semibold text-green-900">{whatIfResult.modified.risk_level}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-green-700">Probability:</span>
                      <span className="font-semibold text-green-900">
                        {(whatIfResult.modified.violation_probability * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Impact */}
                <div className="md:col-span-2 bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 mb-2">Impact Analysis</h3>
                  <p className="text-sm text-blue-800">
                    Risk {whatIfResult.impact.risk_change} by{' '}
                    <span className="font-bold">
                      {Math.abs(whatIfResult.impact.probability_change * 100).toFixed(1)}%
                    </span>
                  </p>
                  <p className="text-xs text-blue-700 mt-1">
                    {whatIfResult.impact.risk_level_change}
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Predictions List */}
        {predictions.length > 0 ? (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
              <h2 className="text-lg font-semibold text-gray-900">
                High-Risk Predictions ({predictions.length})
              </h2>
            </div>
            
            <div className="divide-y divide-gray-200">
              {predictions.map((prediction) => (
                <div
                  key={prediction.id}
                  className="p-6 hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() => setSelectedPrediction(
                    selectedPrediction?.id === prediction.id ? null : prediction
                  )}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-2xl">{getRiskIcon(prediction.risk_level)}</span>
                        <div>
                          <h3 className="font-semibold text-gray-900">{prediction.record_id}</h3>
                          <p className="text-xs text-gray-500">
                            {new Date(prediction.predicted_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className={`inline-block px-3 py-1 rounded-full text-xs font-medium border ${getRiskColor(prediction.risk_level)}`}>
                        {prediction.risk_level.toUpperCase()}
                      </div>
                      <p className="text-2xl font-bold text-gray-900 mt-2">
                        {(prediction.violation_probability * 100).toFixed(0)}%
                      </p>
                      <p className="text-xs text-gray-500">Violation Risk</p>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {selectedPrediction?.id === prediction.id && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      {/* Risk Factors */}
                      <div className="mb-4">
                        <h4 className="font-semibold text-gray-900 mb-2">⚠️ Risk Factors</h4>
                        <ul className="space-y-1">
                          {prediction.risk_factors.map((factor, idx) => (
                            <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                              <span className="text-red-500 mt-1">•</span>
                              <span>{factor}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Recommendations */}
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">💡 Recommendations</h4>
                        <ul className="space-y-1">
                          {prediction.recommendations.map((rec, idx) => (
                            <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                              <span className="text-green-500 mt-1">✓</span>
                              <span>{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Confidence */}
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">Confidence Score</span>
                          <span className="font-semibold text-gray-900">
                            {(prediction.confidence_score * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                          <div
                            className="bg-purple-600 h-2 rounded-full transition-all"
                            style={{ width: `${prediction.confidence_score * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <svg className="w-20 h-20 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Predictions Yet</h3>
            <p className="text-gray-600">Start analyzing records to see ML-powered predictions</p>
          </div>
        )}
      </div>
    </div>
  );
}
