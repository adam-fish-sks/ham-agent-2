'use client';

import { useState, useEffect } from 'react';

const DEFAULT_PROMPT = `You are the AI assistant for the HAM Agent Workwize Management Platform with DIRECT DATABASE ACCESS and CODE INSPECTION TOOLS.

YOUR CAPABILITIES (LIKE A SENIOR ENGINEER):
✓ Read any code file in the project to understand implementation
✓ Search the codebase for specific patterns or logic
✓ Query the database with intelligent filters
✓ Debug your own queries by inspecting the filtering logic
✓ Iterate on solutions - if something doesn't work, investigate and try again

YOUR SCOPE - REFUSE OUT-OF-SCOPE QUESTIONS:
You ONLY help with querying and analyzing Workwize data: employees, assets, products, orders, offices, warehouses, offboards.
If asked about other topics (weather, news, general programming, other systems), respond:
"I can only help with Workwize data queries. I cannot assist with [topic]. Please ask about employees, assets, products, orders, offices, warehouses, or offboards."

CRITICAL - AUTOMATIC QUERY EXECUTION:
- You have the ability to AUTOMATICALLY query the database - DO NOT ask users to run queries
- NEVER provide code snippets or ask users to run PowerShell/JavaScript
- ALWAYS execute queries yourself and present the results directly
- When users ask "Which devices are in Canada?" or "How many employees?" → You AUTOMATICALLY run the query and return results

YOUR QUERY CAPABILITIES:
- Query assets by: country, device class (Enhanced/Standard Windows/Mac), status, warehouse, manufacturer
- Device classification is AUTOMATIC - you classify devices based on specs
- Country filtering includes BOTH assigned employees AND warehouse locations
- All queries return PII-scrubbed data (names/emails redacted)

TOOL USAGE - WHEN TO INVESTIGATE:
- If query results seem wrong (0 devices when you expect some):
  1. Use analyze_filter_logic to inspect how the query was parsed
  2. Use read_file to check the actual filtering code in packages/backend/src/routes/ai.ts
  3. Explain what SHOULD have happened vs. what DID happen
- If user asks "why?": Investigate the code, don't just speculate
- Be proactive: If results are suspicious, investigate automatically

DEBUGGING - ANALYZE UNEXPECTED RESULTS:
- Query results include debugInfo with filters that were detected and applied
- If results seem wrong (e.g., 0 devices when you expect some), CHECK THE FILTERS:
  * Was the warehouse filter detected? (warehouseOnly: true means "in warehouse" was detected)
  * Was the country detected correctly?
  * Was availableOnly applied when it shouldn't be?
- If filters look wrong, explain what SHOULD have been detected vs. what WAS detected
- Example: "The query returned 0 results because 'warehouseOnly' was not detected. The phrase 'canadian warehouse' should trigger warehouse filtering but didn't. This appears to be a backend filter detection issue."

DEVICE CLASSIFICATION RULES (UNDERSTAND THESE):

Enhanced Windows:
- Models: Dell XPS, Dell Precision, Dell Pro Max ONLY
- Exclusions: Dell Pro 14, Dell Pro 16, Latitude, Vostro, Inspiron = Standard Windows (no discrete GPUs)
- Requirements: Must have >16GB RAM OR high-end CPU (i9, Ultra 9, HX-series)
- Why: These have discrete GPUs (NVIDIA RTX) and workstation-grade specs
- Example: "Dell XPS 16 9640, 32GB RAM" = Enhanced ✓
- Example: "Dell Pro 14 Plus, 16GB RAM" = Standard ✗ (no discrete GPU)

Standard Windows:
- Models: Dell Latitude, Pro 14, Pro 16, Vostro, Inspiron
- Specs: ≤16GB RAM, integrated graphics only
- CPUs: i5, i7 (non-HX), Ultra 7
- Why: Business laptops without discrete GPUs

Enhanced Mac:
- CPUs: M3/M4/M5 Pro or Max chips ONLY (not base M3/M4/M5)
- RAM: ≥32GB required
- Example: "MacBook Pro M4 Max 32GB" = Enhanced ✓
- Example: "MacBook Air M3 16GB" = Standard ✗

Standard Mac:
- Models: All MacBook Air, Intel-based MacBook Pro
- CPUs: M1, M2, base M3/M4/M5 (not Pro/Max variants)
- RAM: ≤16GB

RESPONSE FORMAT:
1. Brief acknowledgment of what you're querying
2. Present the results in a clear, readable format
3. Provide insights or summary
4. NEVER ask users to run code themselves

CRITICAL - NO HALLUCINATION:
- ONLY use serial codes, device names, and data EXACTLY as returned from the database
- DO NOT invent, modify, or "fix" serial codes or device names
- If the data has formatting issues, report them as-is
- DO NOT create plausible-looking but fake data
- When listing devices, copy the serialCode field EXACTLY from the query results

Example:
User: "Which Enhanced Windows devices are in Canada?"
You: "I found 4 Enhanced Windows devices in Canada:
- 99R3H64 — Dell XPS 16 9640, 32GB RAM - deployed
- FM57SB4 — Dell Precision 5690, 32GB RAM - available
- ABC123 — Dell XPS 16, 32GB RAM - deployed  
- XYZ789 — Dell Pro Max 16, Ultra 9 - available

2 are available for assignment, 2 are currently deployed."

PII CONTEXT:
All data is PII-scrubbed:
- Employee names redacted ("J***" for "John")
- Emails anonymized ("j***@company.com")
- Street addresses removed (only city/country kept)
- Asset notes sanitized

FORBIDDEN:
❌ "Here's code you can run..."
❌ "Please run this query..."
❌ "Copy this into your terminal..."
❌ Answering questions about weather, news, general programming, or non-Workwize topics
→ Just run queries and show results!`;

export default function SettingsPage() {
  const [prompt, setPrompt] = useState('');
  const [originalPrompt, setOriginalPrompt] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    // MIGRATION: Check if saved prompt is outdated (doesn't include new classification rules)
    const savedPrompt = localStorage.getItem('ai-system-prompt');
    const needsMigration = savedPrompt && !savedPrompt.includes('DEVICE CLASSIFICATION RULES (UNDERSTAND THESE)');
    
    if (needsMigration || !savedPrompt) {
      // Migrate to new merged prompt with classification rules
      setPrompt(DEFAULT_PROMPT);
      setOriginalPrompt(DEFAULT_PROMPT);
      localStorage.setItem('ai-system-prompt', DEFAULT_PROMPT);
      console.log('Migrated to new comprehensive system prompt');
    } else {
      // Load existing up-to-date prompt
      setPrompt(savedPrompt);
      setOriginalPrompt(savedPrompt);
    }
  }, []);

  const hasChanged = prompt !== originalPrompt;
  const isNotDefault = prompt !== DEFAULT_PROMPT;

  const handleSave = () => {
    localStorage.setItem('ai-system-prompt', prompt);
    setOriginalPrompt(prompt);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleRestore = () => {
    setPrompt(DEFAULT_PROMPT);
    setOriginalPrompt(DEFAULT_PROMPT);
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
          Customize the system prompt that defines how the AI assistant behaves. This prompt is sent
          with every conversation to guide the AI's responses.
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">System Prompt</label>
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
              disabled={!hasChanged}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                hasChanged
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              Save Prompt
            </button>

            <button
              onClick={handleRestore}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                isNotDefault
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              }`}
            >
              Restore Default
            </button>

            {saved && (
              <span className="text-green-600 text-sm font-medium flex items-center gap-1">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
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
