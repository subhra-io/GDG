'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

interface Violation {
  id: string;
  record_identifier: string;
  severity: string;
  status: string;
  justification: string;
  detected_at: string;
  risk_score: number;
  assigned_to: string | null;
  assigned_user?: User;
  is_false_positive: boolean;
}

export default function ReviewsPage() {
  const [violations, setViolations] = useState<Violation[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState('pending_review');
  const [filterSeverity, setFilterSeverity] = useState('');
  const [selectedUser, setSelectedUser] = useState('265a4bde-d968-4109-bc48-7cda0fe3d97d'); // John Doe

  useEffect(() => {
    fetchUsers();
    fetchViolations();
  }, [filterStatus, filterSeverity]);

  const fetchUsers = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/reviews/users');
      if (!response.ok) throw new Error('Failed to fetch users');
      const data = await response.json();
      setUsers(data.users || []);
    } catch (err) {
      console.error('Error fetching users:', err);
    }
  };

  const fetchViolations = async () => {
    try {
      setLoading(true);
      let url = `http://localhost:8000/api/v1/reviews/queue?limit=50`;
      if (filterStatus) url += `&status=${filterStatus}`;
      if (filterSeverity) url += `&severity=${filterSeverity}`;
      
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch violations');
      
      const data = await response.json();
      setViolations(data.violations || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const assignViolation = async (violationId: string, userId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/reviews/${violationId}/assign`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
      });
      
      if (!response.ok) throw new Error('Failed to assign violation');
      
      // Refresh list
      fetchViolations();
    } catch (err) {
      alert('Failed to assign: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const submitReview = async (violationId: string, action: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/reviews/${violationId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reviewer_user_id: selectedUser,
          action: action,
          reason: `Quick ${action} from review queue`
        })
      });
      
      if (!response.ok) throw new Error('Failed to submit review');
      
      // Refresh list
      fetchViolations();
    } catch (err) {
      alert('Failed to submit review: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-300';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return '🔴';
      case 'high': return '🟠';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '⚪';
    }
  };

  if (loading && violations.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading review queue...</p>
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
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            <h1 className="text-3xl font-bold text-gray-900">Review Queue</h1>
          </div>
          <p className="text-gray-600">Review and manage compliance violations</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="pending_review">Pending Review</option>
                <option value="confirmed">Confirmed</option>
                <option value="dismissed">Dismissed</option>
                <option value="">All</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Severity</label>
              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Reviewer</label>
              <select
                value={selectedUser}
                onChange={(e) => setSelectedUser(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {users.filter(u => u.role === 'reviewer' || u.role === 'admin').map(user => (
                  <option key={user.id} value={user.id}>{user.name}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Total Pending</p>
            <p className="text-2xl font-bold text-gray-900">{violations.length}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Critical</p>
            <p className="text-2xl font-bold text-red-600">
              {violations.filter(v => v.severity === 'critical').length}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">High</p>
            <p className="text-2xl font-bold text-orange-600">
              {violations.filter(v => v.severity === 'high').length}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Unassigned</p>
            <p className="text-2xl font-bold text-blue-600">
              {violations.filter(v => !v.assigned_to).length}
            </p>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Violations List */}
        {violations.length > 0 ? (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="divide-y divide-gray-200">
              {violations.map((violation) => (
                <div key={violation.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-2xl">{getSeverityIcon(violation.severity)}</span>
                        <div>
                          <h3 className="font-semibold text-gray-900">{violation.record_identifier}</h3>
                          <p className="text-xs text-gray-500">
                            {new Date(violation.detected_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <p className="text-sm text-gray-700 mb-2">{violation.justification}</p>
                      
                      {violation.assigned_user && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                          <span>Assigned to: {violation.assigned_user.name}</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="text-right ml-4">
                      <div className={`inline-block px-3 py-1 rounded-full text-xs font-medium border ${getSeverityColor(violation.severity)}`}>
                        {violation.severity.toUpperCase()}
                      </div>
                      {violation.risk_score && (
                        <p className="text-sm text-gray-600 mt-2">
                          Risk: <span className="font-semibold">{violation.risk_score}/100</span>
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 flex-wrap">
                    {!violation.assigned_to && (
                      <button
                        onClick={() => assignViolation(violation.id, selectedUser)}
                        className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Assign to Me
                      </button>
                    )}
                    
                    {violation.status === 'pending_review' && (
                      <>
                        <button
                          onClick={() => submitReview(violation.id, 'confirm')}
                          className="px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                          ✓ Approve
                        </button>
                        <button
                          onClick={() => submitReview(violation.id, 'dismiss')}
                          className="px-3 py-1.5 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                        >
                          ✗ Reject
                        </button>
                        <button
                          onClick={() => submitReview(violation.id, 'request_more_info')}
                          className="px-3 py-1.5 text-sm bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
                        >
                          ? Request Info
                        </button>
                      </>
                    )}
                    
                    <Link
                      href={`/violations/${violation.id}`}
                      className="px-3 py-1.5 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      View Details →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <svg className="w-20 h-20 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Violations to Review</h3>
            <p className="text-gray-600">All violations have been reviewed</p>
          </div>
        )}
      </div>
    </div>
  );
}
