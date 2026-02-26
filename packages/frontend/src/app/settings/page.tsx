'use client';

import { useState, useEffect } from 'react';

const DEFAULT_PROMPT = `You are a helpful AI assistant for the HAM Agent Workwize Management Platform. 
You have access to a database with cached data from Workwize API.

IMPORTANT: All data in the database has been PII-scrubbed:
- Employee names are redacted (e.g., "J***" for "John")
- Emails are anonymized (e.g., "j***@company.com")
- Street addresses are removed (only city/state kept)
- Asset notes have PII patterns removed

When users ask questions:
1. Analyze what data they need
2. Let them know you'll query the database
3. Provide insights based on the scrubbed data
4. Remind them that names/emails are redacted for privacy

Be helpful and conversational. If you need to query data, explain what you're looking for.`;

export default function SettingsPage() {
  const [prompt, setPrompt] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    // Load custom prompt from localStorage
    const savedPrompt = localStorage.getItem('ai-system-prompt');
    if (savedPrompt) {
      setPrompt(savedPrompt);
    } else {
      setPrompt(DEFAULT_PROMPT);
    }
  }, []);

  const handleSave = () => {
    localStorage.setItem('ai-system-prompt', prompt);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleRestore = () => {
    setPrompt(DEFAULT_PROMPT);
    localStorage.setItem('ai-system-prompt', DEFAULT_PROMPT);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Settings</h1>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">AI Assistant System Prompt</h2>
        
        <p className="text-sm text-gray-600 mb-4">
          Customize the system prompt that defines how the AI assistant behaves. 
          This prompt is sent with every conversation to guide the AI's responses.
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              System Prompt
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={15}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              placeholder="Enter your custom system prompt..."
            />
            <p className="mt-2 text-xs text-gray-500">
              The database context will be automatically appended to this prompt.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleSave}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
            >
              Save Prompt
            </button>
            
            <button
              onClick={handleRestore}
              className="px-6 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
            >
              Restore Default
            </button>

            {saved && (
              <span className="text-green-600 text-sm font-medium flex items-center gap-1">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Saved!
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="text-yellow-900 font-semibold mb-2">💡 Tips:</h3>
        <ul className="text-yellow-800 text-sm space-y-1">
          <li>• Be specific about the AI's role and capabilities</li>
          <li>• Include important context about data limitations</li>
          <li>• Define the tone and style of responses</li>
          <li>• Clear the AI chat history after changing the prompt for best results</li>
        </ul>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-blue-900 font-semibold mb-2">📝 Default Prompt Preview:</h3>
        <pre className="text-xs text-blue-800 whitespace-pre-wrap font-mono bg-white p-3 rounded border border-blue-200">
{DEFAULT_PROMPT}
        </pre>
      </div>
    </div>
  );
}
