'use client';

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function AIAssistantPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load messages from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('ai-chat-history');
    if (saved) {
      try {
        setMessages(JSON.parse(saved));
      } catch (error) {
        console.error('Failed to load chat history:', error);
        // Set default message if parsing fails
        setMessages([
          {
            role: 'assistant',
            content:
              "Hello! I'm your AI assistant for the Workwize management platform. I can help you query and analyze your cached data. What would you like to know?",
          },
        ]);
      }
    } else {
      // Set default message if no history
      setMessages([
        {
          role: 'assistant',
          content:
            "Hello! I'm your AI assistant for the Workwize management platform. I can help you query and analyze your cached data. What would you like to know?",
        },
      ]);
    }
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('ai-chat-history', JSON.stringify(messages));
    }
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Load custom prompt from localStorage - always required
      let customPrompt = localStorage.getItem('ai-system-prompt');
      
      // If no prompt saved, user needs to configure it in settings
      if (!customPrompt) {
        const errorMessage: Message = {
          role: 'assistant',
          content: 'Please configure the AI system prompt in Settings before using the assistant.',
        };
        setMessages((prev) => [...prev, errorMessage]);
        setLoading(false);
        return;
      }

      const response = await axios.post('http://localhost:3001/api/ai/chat', {
        message: input,
        history: messages,
        customPrompt,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.message}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearHistory = () => {
    const defaultMessage: Message = {
      role: 'assistant',
      content:
        "Hello! I'm your AI assistant for the Workwize management platform. I can help you query and analyze your cached data. What would you like to know?",
    };
    setMessages([defaultMessage]);
    localStorage.setItem('ai-chat-history', JSON.stringify([defaultMessage]));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">AI Assistant</h1>
        <button
          onClick={clearHistory}
          className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
        >
          Clear History
        </button>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-blue-900 font-semibold mb-2">🤖 AI Assistant Features:</h3>
        <ul className="text-blue-800 text-sm space-y-1">
          <li>• Query employees, assets, orders, and other data</li>
          <li>• Get statistics and insights about your data</li>
          <li>• All responses use PII-scrubbed cached data</li>
          <li>• Powered by Azure OpenAI</li>
        </ul>
      </div>

      <div className="bg-white rounded-lg shadow flex flex-col h-[600px]">
        {/* Messages area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-4 ${
                  message.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="text-sm whitespace-pre-wrap">{message.content}</div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg p-4">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.1s' }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.2s' }}
                  ></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="border-t p-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your Workwize data..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className={`px-6 py-2 rounded-lg font-medium ${
                loading || !input.trim()
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              }`}
            >
              Send
            </button>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="text-yellow-900 font-semibold mb-2">🔒 Privacy Note:</h3>
        <p className="text-yellow-800 text-sm">
          The AI assistant only has access to PII-scrubbed cached data. All employee names, emails,
          and sensitive information have been redacted before storage.
        </p>
      </div>
    </div>
  );
}
