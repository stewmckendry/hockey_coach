import React from 'react'
import { useChat } from '../hooks/useChat'

/**
 * Example secure chat component demonstrating the new architecture
 */
export function SecureChatDemo() {
  const { messages, isLoading, sendMessage, clearMessages } = useChat()

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const message = formData.get('message') as string
    if (message.trim()) {
      sendMessage(message.trim())
      e.currentTarget.reset()
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Header */}
        <div className="bg-blue-600 text-white p-4">
          <h2 className="text-xl font-semibold">🏒 Secure Hockey Coach Assistant</h2>
          <p className="text-blue-100 text-sm mt-1">
            Powered by secure server-side LLM • API keys protected • Rate limited
          </p>
        </div>

        {/* Messages */}
        <div className="h-96 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              <div className="text-4xl mb-2">🥅</div>
              <p>Ask me anything about hockey coaching!</p>
              <p className="text-sm mt-2">Try: "Plan a U10 practice focused on skating"</p>
            </div>
          )}
          
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
                
                {/* Metadata Display */}
                {message.metadata && (
                  <div className="text-xs opacity-70 mt-2 border-t pt-2">
                    {message.metadata.intent && (
                      <div>Intent: {message.metadata.intent.intent} ({Math.round(message.metadata.intent.confidence * 100)}%)</div>
                    )}
                    {message.metadata.toolsCalled && (
                      <div>Tools: {message.metadata.toolsCalled.join(', ')}</div>
                    )}
                    {message.metadata.processingTime && (
                      <div>Processed in {message.metadata.processingTime}ms</div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg px-4 py-2">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                  <span className="text-gray-600">Coach is thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Form */}
        <div className="border-t p-4">
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <input
              name="message"
              type="text"
              placeholder="Ask about drills, practice plans, player development..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading}
              className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg font-medium"
            >
              Send
            </button>
          </form>
          
          <div className="flex justify-between items-center mt-3">
            <button
              onClick={clearMessages}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Clear Chat
            </button>
            
            <div className="text-xs text-gray-500">
              🔒 Secure • Messages processed server-side
            </div>
          </div>
        </div>
      </div>

      {/* Security Features Display */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="text-green-500 text-xl mr-2">🔐</div>
            <div>
              <h3 className="font-medium text-green-900">API Keys Protected</h3>
              <p className="text-sm text-green-700">OpenAI key stays on server</p>
            </div>
          </div>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="text-blue-500 text-xl mr-2">🛡️</div>
            <div>
              <h3 className="font-medium text-blue-900">Rate Limited</h3>
              <p className="text-sm text-blue-700">10 requests per hour</p>
            </div>
          </div>
        </div>
        
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="text-purple-500 text-xl mr-2">🕵️‍♂️</div>
            <div>
              <h3 className="font-medium text-purple-900">Logic Protected</h3>
              <p className="text-sm text-purple-700">Prompts stay private</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
