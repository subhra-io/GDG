'use client';

import { useState, useEffect } from 'react';
import { FileText, Filter, Download, Search, Eye, Clock, User, Activity } from 'lucide-react';

interface AuditLog {
  id: string;
  timestamp: string;
  event_type: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  user_email: string | null;
  ip_address: string | null;
  request_method: string | null;
  request_path: string | null;
  response_status: number | null;
  duration_ms: number | null;
  ai_model: string | null;
  ai_confidence: number | null;
}

export default function AuditTrailPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  
  // Filters
  const [eventType, setEventType] = useState<string>('');
  const [action, setAction] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [limit, setLimit] = useState<number>(50);

  useEffect(() => {
    fetchLogs();
    fetchStatistics();
  }, [eventType, action, limit]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      let url = `http://localhost:8000/api/v1/audit/logs?limit=${limit}`;
      if (eventType) url += `&event_type=${eventType}`;
      if (action) url += `&action=${action}`;
      
      const response = await fetch(url);
      const data = await response.json();
      setLogs(data.logs || []);
    } catch (error) {
      console.error('Error fetching audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/audit/statistics');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };

  const exportToCSV = async () => {
    try {
      let url = 'http://localhost:8000/api/v1/audit/export/csv?limit=10000';
      if (eventType) url += `&event_type=${eventType}`;
      
      const response = await fetch(url);
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = 'audit_logs.csv';
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (error) {
      console.error('Error exporting logs:', error);
    }
  };

  const getEventTypeColor = (type: string) => {
    switch (type) {
      case 'user_action': return 'bg-blue-100 text-blue-800';
      case 'ai_decision': return 'bg-purple-100 text-purple-800';
      case 'system_event': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'create': return 'bg-green-100 text-green-800';
      case 'read': return 'bg-blue-100 text-blue-800';
      case 'update': return 'bg-yellow-100 text-yellow-800';
      case 'delete': return 'bg-red-100 text-red-800';
      case 'execute': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const filteredLogs = logs.filter(log => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      log.user_email?.toLowerCase().includes(search) ||
      log.resource_type?.toLowerCase().includes(search) ||
      log.request_path?.toLowerCase().includes(search) ||
      log.ip_address?.toLowerCase().includes(search)
    );
  });

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <FileText className="w-8 h-8" />
            Audit Trail
          </h1>
          <p className="mt-2 text-gray-600">
            Complete audit log of all system activities
          </p>
        </div>

        {/* Statistics */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                <Activity className="w-4 h-4" />
                Total Events
              </div>
              <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-sm text-gray-600 mb-1">User Actions</div>
              <div className="text-2xl font-bold text-blue-600">
                {stats.by_event_type?.user_action || 0}
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-sm text-gray-600 mb-1">AI Decisions</div>
              <div className="text-2xl font-bold text-purple-600">
                {stats.by_event_type?.ai_decision || 0}
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-sm text-gray-600 mb-1">System Events</div>
              <div className="text-2xl font-bold text-gray-600">
                {stats.by_event_type?.system_event || 0}
              </div>
            </div>
          </div>
        )}

        {/* Filters and Actions */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">Filters:</span>
            </div>
            
            <select
              value={eventType}
              onChange={(e) => setEventType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            >
              <option value="">All Event Types</option>
              <option value="user_action">User Actions</option>
              <option value="ai_decision">AI Decisions</option>
              <option value="system_event">System Events</option>
            </select>
            
            <select
              value={action}
              onChange={(e) => setAction(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            >
              <option value="">All Actions</option>
              <option value="create">Create</option>
              <option value="read">Read</option>
              <option value="update">Update</option>
              <option value="delete">Delete</option>
              <option value="execute">Execute</option>
            </select>
            
            <select
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            >
              <option value="50">50 logs</option>
              <option value="100">100 logs</option>
              <option value="500">500 logs</option>
              <option value="1000">1000 logs</option>
            </select>
            
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search logs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>
            </div>
            
            <button
              onClick={exportToCSV}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2 text-sm"
            >
              <Download className="w-4 h-4" />
              Export CSV
            </button>
          </div>
        </div>

        {/* Audit Logs Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="p-12 text-center text-gray-500">
              Loading audit logs...
            </div>
          ) : filteredLogs.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg">No audit logs found</p>
              <p className="text-sm mt-2">Try adjusting your filters</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Timestamp
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Event Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Action
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Resource
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Duration
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-gray-400" />
                          {formatTimestamp(log.timestamp)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded ${getEventTypeColor(log.event_type)}`}>
                          {log.event_type.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded ${getActionColor(log.action)}`}>
                          {log.action}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {log.resource_type || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        <div className="flex items-center gap-2">
                          <User className="w-4 h-4 text-gray-400" />
                          {log.user_email || 'System'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {log.response_status && (
                          <span className={`px-2 py-1 text-xs font-medium rounded ${
                            log.response_status < 300 ? 'bg-green-100 text-green-800' :
                            log.response_status < 400 ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {log.response_status}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {log.duration_ms ? `${log.duration_ms}ms` : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => setSelectedLog(log)}
                          className="text-blue-600 hover:text-blue-700 flex items-center gap-1"
                        >
                          <Eye className="w-4 h-4" />
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Detail Modal */}
        {selectedLog && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">Audit Log Detail</h2>
                  <button
                    onClick={() => setSelectedLog(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm font-medium text-gray-500">Event Type</div>
                      <div className="mt-1">
                        <span className={`px-2 py-1 text-xs font-medium rounded ${getEventTypeColor(selectedLog.event_type)}`}>
                          {selectedLog.event_type.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-500">Action</div>
                      <div className="mt-1">
                        <span className={`px-2 py-1 text-xs font-medium rounded ${getActionColor(selectedLog.action)}`}>
                          {selectedLog.action}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="text-sm font-medium text-gray-500">Timestamp</div>
                    <div className="mt-1 text-sm text-gray-900">{formatTimestamp(selectedLog.timestamp)}</div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm font-medium text-gray-500">Resource Type</div>
                      <div className="mt-1 text-sm text-gray-900">{selectedLog.resource_type || '-'}</div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-500">Resource ID</div>
                      <div className="mt-1 text-sm text-gray-900 font-mono text-xs">
                        {selectedLog.resource_id || '-'}
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="text-sm font-medium text-gray-500">User</div>
                    <div className="mt-1 text-sm text-gray-900">{selectedLog.user_email || 'System'}</div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm font-medium text-gray-500">IP Address</div>
                      <div className="mt-1 text-sm text-gray-900">{selectedLog.ip_address || '-'}</div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-500">Duration</div>
                      <div className="mt-1 text-sm text-gray-900">
                        {selectedLog.duration_ms ? `${selectedLog.duration_ms}ms` : '-'}
                      </div>
                    </div>
                  </div>
                  
                  {selectedLog.request_method && (
                    <div>
                      <div className="text-sm font-medium text-gray-500">Request</div>
                      <div className="mt-1 text-sm text-gray-900">
                        <span className="font-mono bg-gray-100 px-2 py-1 rounded">
                          {selectedLog.request_method}
                        </span>
                        {' '}
                        <span className="text-gray-600">{selectedLog.request_path}</span>
                      </div>
                    </div>
                  )}
                  
                  {selectedLog.response_status && (
                    <div>
                      <div className="text-sm font-medium text-gray-500">Response Status</div>
                      <div className="mt-1">
                        <span className={`px-2 py-1 text-xs font-medium rounded ${
                          selectedLog.response_status < 300 ? 'bg-green-100 text-green-800' :
                          selectedLog.response_status < 400 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {selectedLog.response_status}
                        </span>
                      </div>
                    </div>
                  )}
                  
                  {selectedLog.ai_model && (
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm font-medium text-gray-500">AI Model</div>
                        <div className="mt-1 text-sm text-gray-900">{selectedLog.ai_model}</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-500">Confidence</div>
                        <div className="mt-1 text-sm text-gray-900">
                          {selectedLog.ai_confidence ? `${(selectedLog.ai_confidence * 100).toFixed(1)}%` : '-'}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="mt-6 flex justify-end">
                  <button
                    onClick={() => setSelectedLog(null)}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
