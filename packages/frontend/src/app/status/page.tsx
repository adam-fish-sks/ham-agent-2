'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';

interface EndpointStatus {
  name: string;
  endpoint: string;
  status: 'healthy' | 'degraded' | 'down';
  responseTime: number | null;
  error?: string;
  statusCode?: number;
}

interface WorkwizeStatus {
  overall: 'healthy' | 'degraded' | 'down';
  lastChecked: string;
  endpoints: EndpointStatus[];
  error?: string;
}

interface DatabaseStatus {
  status: 'healthy' | 'down';
  responseTime: number;
  lastChecked: string;
  error?: string;
}

export default function StatusPage() {
  const [workwizeStatus, setWorkwizeStatus] = useState<WorkwizeStatus | null>(null);
  const [databaseStatus, setDatabaseStatus] = useState<DatabaseStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const loadStatus = async () => {
    try {
      setLoading(true);
      setError(null);

      const [workwizeRes, databaseRes] = await Promise.all([
        axios.get('http://localhost:3001/api/status/workwize'),
        axios.get('http://localhost:3001/api/status/database'),
      ]);

      setWorkwizeStatus(workwizeRes.data);
      setDatabaseStatus(databaseRes.data);
    } catch (err: any) {
      setError(err.message || 'Failed to load status');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();

    // Auto-refresh every 30 seconds if enabled
    let interval: NodeJS.Timeout | null = null;
    if (autoRefresh) {
      interval = setInterval(loadStatus, 30000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const getStatusColor = (status: 'healthy' | 'degraded' | 'down') => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'down':
        return 'bg-red-100 text-red-800 border-red-300';
    }
  };

  const getStatusIcon = (status: 'healthy' | 'degraded' | 'down') => {
    switch (status) {
      case 'healthy':
        return '✓';
      case 'degraded':
        return '⚠';
      case 'down':
        return '✗';
    }
  };

  const formatResponseTime = (ms: number | null) => {
    if (ms === null) return 'Timeout';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const formatTimestamp = (iso: string) => {
    const date = new Date(iso);
    return date.toLocaleString();
  };

  if (loading && !workwizeStatus && !databaseStatus) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-xl text-gray-600">Loading status...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">API Status Monitor</h1>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            Auto-refresh (30s)
          </label>
          <button
            onClick={loadStatus}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 text-sm font-medium"
          >
            {loading ? 'Refreshing...' : 'Refresh Now'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h2 className="text-red-800 font-semibold">Error</h2>
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Overall Status Card */}
      {workwizeStatus && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Workwize APIs</h2>
              <p className="text-sm text-gray-600">
                Last checked: {formatTimestamp(workwizeStatus.lastChecked)}
              </p>
            </div>
            <div
              className={`px-6 py-3 rounded-lg border-2 ${getStatusColor(workwizeStatus.overall)}`}
            >
              <div className="text-2xl font-bold text-center">
                {getStatusIcon(workwizeStatus.overall)} {workwizeStatus.overall.toUpperCase()}
              </div>
            </div>
          </div>
          {workwizeStatus.error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded">
              <p className="text-sm text-red-800 font-semibold mb-1">Configuration Error</p>
              <p className="text-sm text-red-700">{workwizeStatus.error}</p>
            </div>
          )}
        </div>
      )}

      {/* Workwize Endpoints */}
      {workwizeStatus && workwizeStatus.endpoints.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Endpoint Details</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    API Endpoint
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Response Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    HTTP Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Error
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {workwizeStatus.endpoints.map((endpoint) => (
                  <tr key={endpoint.endpoint} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${getStatusColor(endpoint.status)}`}
                      >
                        {getStatusIcon(endpoint.status)} {endpoint.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{endpoint.name}</div>
                      <div className="text-xs text-gray-500 font-mono">{endpoint.endpoint}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {endpoint.responseTime !== null ? (
                        <span
                          className={
                            endpoint.responseTime > 3000
                              ? 'text-red-600 font-semibold'
                              : endpoint.responseTime > 1000
                                ? 'text-yellow-600 font-semibold'
                                : 'text-green-600'
                          }
                        >
                          {formatResponseTime(endpoint.responseTime)}
                        </span>
                      ) : (
                        <span className="text-red-600 font-semibold">Timeout</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {endpoint.statusCode || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-red-600">
                      {endpoint.error && (
                        <span className="font-mono text-xs">{endpoint.error}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Database Status */}
      {databaseStatus && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">PostgreSQL Database</h2>
              <p className="text-sm text-gray-600">
                Last checked: {formatTimestamp(databaseStatus.lastChecked)}
              </p>
              {databaseStatus.responseTime && (
                <p className="text-sm text-gray-600 mt-1">
                  Response time:{' '}
                  <span className="font-semibold text-green-600">
                    {formatResponseTime(databaseStatus.responseTime)}
                  </span>
                </p>
              )}
            </div>
            <div
              className={`px-6 py-3 rounded-lg border-2 ${getStatusColor(databaseStatus.status)}`}
            >
              <div className="text-2xl font-bold text-center">
                {getStatusIcon(databaseStatus.status)} {databaseStatus.status.toUpperCase()}
              </div>
            </div>
          </div>
          {databaseStatus.error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
              <p className="text-sm text-red-800 font-mono">{databaseStatus.error}</p>
            </div>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Status Legend</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-green-600 text-lg">✓</span>
            <div>
              <span className="font-semibold">Healthy:</span> API responding normally (&lt;1s)
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-yellow-600 text-lg">⚠</span>
            <div>
              <span className="font-semibold">Degraded:</span> Slow response (1-3s) or partial
              failures
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-red-600 text-lg">✗</span>
            <div>
              <span className="font-semibold">Down:</span> Not responding or timeout (&gt;10s)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
