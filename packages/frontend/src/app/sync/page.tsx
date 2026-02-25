'use client';

import { useState } from 'react';
import axios from 'axios';

export default function SyncPage() {
  const [syncing, setSyncing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const syncAll = async () => {
    try {
      setSyncing(true);
      setError(null);
      setResults(null);

      const response = await axios.post('http://localhost:3001/api/sync/all');
      setResults(response.data);
    } catch (err: any) {
      setError(err.message || 'Sync failed');
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Sync Data from Workwize</h1>

      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600 mb-4">
          Synchronize all data from the Workwize API to the local cache. 
          All PII will be automatically scrubbed during the sync process.
        </p>

        <button
          onClick={syncAll}
          disabled={syncing}
          className={`px-6 py-3 rounded-md font-medium ${
            syncing
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          {syncing ? 'Syncing...' : 'Sync All Data'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h2 className="text-red-800 font-semibold">Error</h2>
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {results && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Sync Results</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(results).map(([entity, result]: [string, any]) => (
              <div key={entity} className="border rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 capitalize mb-2">
                  {entity}
                </h3>
                <div className="text-sm text-gray-600">
                  <div>Synced: <span className="font-medium text-green-600">{result.synced || 0}</span></div>
                  {result.failed > 0 && (
                    <div>Failed: <span className="font-medium text-red-600">{result.failed}</span></div>
                  )}
                  {result.total && (
                    <div>Total: <span className="font-medium">{result.total}</span></div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-blue-900 font-semibold mb-2">📋 What gets synced:</h3>
        <ul className="text-blue-800 text-sm space-y-1">
          <li>• Employees (names and emails scrubbed)</li>
          <li>• Assets (PII removed from notes and locations)</li>
          <li>• Orders</li>
          <li>• Products</li>
          <li>• Offices</li>
          <li>• Warehouses</li>
          <li>• Offboards</li>
        </ul>
      </div>
    </div>
  );
}
