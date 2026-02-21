'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';

interface MonitoringStatus {
  is_monitoring_active: boolean;
  last_scan_time: string | null;
  last_scan_status: string | null;
  violations_found_last_scan: number | null;
  records_scanned_last_scan: number | null;
  total_scans_today: number;
  next_scheduled_scan: string | null;
}

export default function MonitoringStatus() {
  const [status, setStatus] = useState<MonitoringStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);

  const fetchStatus = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/monitoring/status');
      setStatus(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch monitoring status:', error);
      setLoading(false);
    }
  };

  const triggerScan = async () => {
    setScanning(true);
    try {
      await axios.post('http://localhost:8000/api/v1/monitoring/scan');
      // Refresh status after 2 seconds
      setTimeout(() => {
        fetchStatus();
        setScanning(false);
      }, 2000);
    } catch (error) {
      console.error('Failed to trigger scan:', error);
      setScanning(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-500">Failed to load monitoring status</p>
      </div>
    );
  }

  const formatTime = (timeStr: string | null) => {
    if (!timeStr) return 'Never';
    const date = new Date(timeStr);
    return date.toLocaleString();
  };

  const getStatusColor = (isActive: boolean) => {
    return isActive ? 'text-green-600' : 'text-gray-400';
  };

  const getStatusBadge = (isActive: boolean) => {
    return isActive
      ? 'bg-green-100 text-green-800'
      : 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${status.is_monitoring_active ? 'bg-green-500 animate-pulse' : 'bg-gray-300'}`}></div>
          <h2 className="text-xl font-semibold text-gray-900">
            Continuous Monitoring
          </h2>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusBadge(status.is_monitoring_active)}`}>
          {status.is_monitoring_active ? 'Active' : 'Idle'}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Last Scan</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatTime(status.last_scan_time)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Status: {status.last_scan_status || 'N/A'}
          </p>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Violations Found</p>
          <p className="text-lg font-semibold text-gray-900">
            {status.violations_found_last_scan ?? 'N/A'}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Last scan
          </p>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Records Scanned</p>
          <p className="text-lg font-semibold text-gray-900">
            {status.records_scanned_last_scan ?? 'N/A'}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Last scan
          </p>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Scans Today</p>
          <p className="text-lg font-semibold text-gray-900">
            {status.total_scans_today}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Automatic + Manual
          </p>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Next Scheduled Scan</p>
          <p className="text-lg font-semibold text-gray-900">
            {status.next_scheduled_scan ? formatTime(status.next_scheduled_scan) : 'N/A'}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Every 5 minutes
          </p>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 flex items-center justify-center">
          <button
            onClick={triggerScan}
            disabled={scanning}
            className={`px-6 py-2 rounded-lg font-medium transition-colors ${
              scanning
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {scanning ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Scanning...
              </span>
            ) : (
              'Scan Now'
            )}
          </button>
        </div>
      </div>

      <div className="border-t pt-4">
        <p className="text-sm text-gray-600">
          <span className="font-medium">Monitoring Mode:</span> Continuous background scanning every 5 minutes
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Powered by Celery + Redis for production-grade async processing
        </p>
      </div>
    </div>
  );
}
