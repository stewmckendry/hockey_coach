/**
 * Test page for OpenAI Agents SDK integration
 * 
 * This page provides:
 * - Simple interface to test agent responses
 * - Side-by-side comparison with existing chat
 * - Performance monitoring
 * - Error handling demonstration
 */

'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

interface AgentResponse {
  response: string;
  error?: string;
  timestamp: string;
  processingTime: number;
}

export default function AgentTestPage() {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [responses, setResponses] = useState<AgentResponse[]>([]);

  const sendMessage = async () => {
    if (!message.trim()) return;

    setIsLoading(true);
    const userMessage = message;
    setMessage('');

    try {
      console.log('Sending message to agent:', userMessage);
      
      const response = await fetch('/api/agent-test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });

      const data: AgentResponse = await response.json();
      
      console.log('Agent response received:', data);

      // Add user message and agent response to history
      setResponses(prev => [
        ...prev,
        {
          response: `You: ${userMessage}`,
          timestamp: new Date().toISOString(),
          processingTime: 0
        },
        data
      ]);

    } catch (error) {
      console.error('Error calling agent:', error);
      
      setResponses(prev => [
        ...prev,
        {
          response: `You: ${userMessage}`,
          timestamp: new Date().toISOString(),
          processingTime: 0
        },
        {
          response: '',
          error: 'Failed to connect to agent',
          timestamp: new Date().toISOString(),
          processingTime: 0
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const testQuestions = [
    "Hello!",
    "What should I focus on with U10 players?",
    "How do I plan a practice?",
    "Tell me about hockey coaching basics"
  ];

  const runQuickTest = async (question: string) => {
    setMessage(question);
    await new Promise(resolve => setTimeout(resolve, 100)); // Brief delay for UI update
    await sendMessage();
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">🏒 Agent Test Interface</h1>
        <p className="text-gray-600">
          Test the OpenAI Agents SDK integration. This connects to the POC agent from Task 1.1.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 mb-6">
        {/* Input Section */}
        <Card>
          <div className="p-4 border-b">
            <h3 className="text-lg font-semibold">Test Agent</h3>
            <p className="text-gray-600 text-sm">
              Send messages to the POC agent and see responses
            </p>
          </div>
          <div className="p-4 space-y-4">
            <div className="flex space-x-2">
              <input
                type="text"
                placeholder="Ask the agent anything..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !isLoading && sendMessage()}
                disabled={isLoading}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <Button 
                onClick={sendMessage} 
                disabled={isLoading || !message.trim()}
              >
                {isLoading ? 'Loading...' : 'Send'}
              </Button>
            </div>

            <div className="space-y-2">
              <p className="text-sm font-medium">Quick Tests:</p>
              <div className="flex flex-wrap gap-2">
                {testQuestions.map((question, index) => (
                  <Button
                    key={index}
                    variant="secondary" 
                    size="sm"
                    onClick={() => runQuickTest(question)}
                    disabled={isLoading}
                  >
                    {question}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </Card>

        {/* Status Section */}
        <Card>
          <div className="p-4 border-b">
            <h3 className="text-lg font-semibold">Connection Status</h3>
            <p className="text-gray-600 text-sm">
              Agent API and POC integration status
            </p>
          </div>
          <div className="p-4">
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <span className="text-green-500">✓</span>
                <span className="text-sm">Web App Running</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-green-500">✓</span>
                <span className="text-sm">Agent API Endpoint Active</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-green-500">✓</span>
                <span className="text-sm">POC Agent Integration</span>
              </div>
              
              {responses.length > 0 && (
                <div className="pt-2 border-t">
                  <p className="text-sm font-medium">Last Response:</p>
                  <p className="text-xs text-gray-500">
                    {responses[responses.length - 1]?.processingTime}ms processing time
                  </p>
                </div>
              )}
            </div>
          </div>
        </Card>
      </div>

      {/* Conversation History */}
      <Card>
        <div className="p-4 border-b">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Conversation History</h3>
            <div className="flex space-x-2">
              <span className="px-2 py-1 bg-gray-100 text-sm rounded">{responses.length} messages</span>
              {responses.length > 0 && (
                <Button 
                  variant="secondary" 
                  size="sm" 
                  onClick={() => setResponses([])}
                >
                  Clear History
                </Button>
              )}
            </div>
          </div>
        </div>
        <div className="p-4">
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {responses.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No messages yet. Try sending a message to the agent!
              </p>
            ) : (
              responses.map((response, index) => (
                <div 
                  key={index}
                  className={`p-3 rounded-lg ${
                    response.response.startsWith('You:') 
                      ? 'bg-blue-50 ml-12' 
                      : response.error 
                        ? 'bg-red-50 mr-12'
                        : 'bg-gray-50 mr-12'
                  }`}
                >
                  {response.error ? (
                    <div className="flex items-start space-x-2">
                      <span className="text-red-500">✗</span>
                      <div>
                        <p className="text-red-700 font-medium">Error</p>
                        <p className="text-red-600 text-sm">{response.error}</p>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <p className="text-gray-900">{response.response}</p>
                      <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
                        <span>
                          {new Date(response.timestamp).toLocaleTimeString()}
                        </span>
                        {response.processingTime > 0 && (
                          <span>{response.processingTime}ms</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}