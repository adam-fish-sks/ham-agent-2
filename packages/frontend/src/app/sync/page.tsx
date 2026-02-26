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
      <h1 className="text-3xl font-bold text-gray-900">Populate Data from Workwize</h1>

      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600 mb-4">
          Synchronize all data from the Workwize API to the local database using Python population scripts. 
          All PII will be automatically scrubbed during the sync process. This process includes fetching 
          employee addresses, warehouse countries, and creating proper address relationships.
        </p>
        
        <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-4">
          <p className="text-sm text-yellow-800">
            ⚠️ <strong>Note:</strong> This process may take 5-10 minutes to complete. 
            The scripts run sequentially and fetch data from the Workwize API with proper error handling.
          </p>
        </div>

        <button
          onClick={syncAll}
          disabled={syncing}
          className={`px-6 py-3 rounded-md font-medium ${
            syncing
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          {syncing ? 'Populating Data...' : 'Populate All Data'}
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
          <h2 className="text-xl font-bold text-gray-900 mb-4">Population Results</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(results).map(([entity, result]: [string, any]) => (
              <div 
                key={entity} 
                className={`border rounded-lg p-4 ${
                  result.status === 'error' ? 'bg-red-50 border-red-200' : 
                  result.status === 'success' ? 'bg-green-50 border-green-200' : 
                  'bg-gray-50 border-gray-200'
                }`}
              >
                <h3 className="font-semibold text-gray-900 capitalize mb-2 flex items-center gap-2">
                  {result.status === 'success' && <span className="text-green-600">✓</span>}
                  {result.status === 'error' && <span className="text-red-600">✗</span>}
                  {entity}
                </h3>
                <div className="text-sm text-gray-600">
                  {result.status === 'success' && (
                    <>
                      <div>Synced: <span className="font-medium text-green-600">{result.synced || 0}</span></div>
                      {result.total && (
                        <div>Total: <span className="font-medium">{result.total}</span></div>
                      )}
                    </>
                  )}
                  {result.status === 'error' && (
                    <div className="text-red-600">
                      <div className="font-medium">Failed</div>
                      <div className="text-xs mt-1">{result.error}</div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-blue-900 font-semibold mb-2">📋 What gets populated:</h3>
        <ul className="text-blue-800 text-sm space-y-1">
          <li>• <strong>Employees</strong> with complete address data (names and emails scrubbed)</li>
          <li>• <strong>Employee Addresses</strong> including country, city, postal code</li>
          <li>• <strong>Assets</strong> with relationships to employees/warehouses/offices (PII removed from notes)</li>
          <li>• <strong>Warehouses</strong> with address data and country information</li>
          <li>• <strong>Warehouse Addresses</strong> from countries array</li>
          <li>• <strong>Orders</strong> with employee and warehouse relationships</li>
          <li>• <strong>Products</strong> catalog data</li>
          <li>• <strong>Offices</strong> location data</li>
          <li>• <strong>Offboards</strong> employee offboarding records</li>
        </ul>
        
        <div className="mt-3 pt-3 border-t border-blue-300">
          <p className="text-xs text-blue-700">
            <strong>Technical Note:</strong> Uses Python population scripts from db-build-scripts/ 
            with proper address fetching from /employees/{'{id}'}/addresses and /warehouses?include=countries APIs.
          </p>
        </div>
      </div>
    </div>
  );
}
