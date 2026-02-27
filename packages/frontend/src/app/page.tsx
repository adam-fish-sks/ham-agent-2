export default function Home() {
  return (
    <div className="space-y-8">
      <div className="bg-white rounded-lg shadow p-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          HAM Agent - Workwize Management Platform
        </h1>
        <p className="text-lg text-gray-600 mb-6">
          Hardware Asset Management with AI assistance and PII-scrubbed data caching
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-2">🔒 PII Scrubbed</h2>
            <p className="text-gray-600">
              All cached data is automatically scrubbed of personally identifiable information
            </p>
          </div>

          <div className="border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-2">📊 Asset Management</h2>
            <p className="text-gray-600">Track employees, assets, orders, and more from Workwize</p>
          </div>

          <div className="border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-2">🤖 AI Assistant</h2>
            <p className="text-gray-600">Chat with AI to query and analyze your data</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Quick Links</h2>
        <div className="space-y-2">
          <a href="/assets" className="block text-blue-600 hover:underline">
            → View Assets
          </a>
          <a href="/ai-assistant" className="block text-blue-600 hover:underline">
            → AI Assistant
          </a>
          <a href="/sync" className="block text-blue-600 hover:underline">
            → Sync Data from Workwize
          </a>
        </div>
      </div>
    </div>
  );
}
