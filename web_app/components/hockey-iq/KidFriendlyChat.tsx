'use client'

import { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Category } from './HockeyIQInterface'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  responseId?: string  // OpenAI Responses API conversation tracking
}

interface KidFriendlyChatProps {
  selectedCategory: Category | null
  embedded?: boolean
}

export interface KidFriendlyChatRef {
  setInputValue: (value: string) => void
}

/**
 * Kid-friendly chat interface for Q&A mode
 * Uses Socratic questioning to help U10 players learn
 */
export const KidFriendlyChat = forwardRef<KidFriendlyChatRef, KidFriendlyChatProps>(
  ({ selectedCategory, embedded = false }, ref) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hi there, hockey star! 🏒 I'm your Hockey IQ Coach! Ask me anything about hockey - rules, skills, positions, or just fun stuff! What would you like to know?",
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [previousResponseId, setPreviousResponseId] = useState<string | undefined>(undefined)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Expose setInput method to parent component
  useImperativeHandle(ref, () => ({
    setInputValue: (value: string) => setInput(value)
  }))

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Use OpenAI Responses API with native conversation tracking
      const response = await fetch('/api/hockey-iq/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          category: selectedCategory,
          age_group: 'U10',
          mode: 'socratic',
          previousResponseId  // Send previous response ID for conversation continuity
        })
      })

      const data = await response.json()
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || "That's a great question! Let me think about that... 🤔",
        timestamp: new Date(),
        responseId: data.responseId  // Store the response ID
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Update the previous response ID for the next turn
      if (data.responseId) {
        setPreviousResponseId(data.responseId)
      }
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "Oops! Something went wrong. Can you try asking that again? 😊",
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const quickQuestions = [
    "What's offside? 🏒",
    "How do I skate faster? ⛸️",
    "Why do we have penalties? ⚖️",
    "What's a hat trick? 🎩",
    "How can I be a better teammate? 🤝"
  ]

  // Reset conversation (clear history and response ID)
  const resetConversation = () => {
    setMessages([
      {
        id: Date.now().toString(),
        role: 'assistant',
        content: "Let's start fresh! 🏒 What would you like to know about hockey?",
        timestamp: new Date()
      }
    ])
    setPreviousResponseId(undefined)
    setInput('')
  }

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto">
      {/* Quick Questions */}
      {messages.length === 1 && (
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2 text-center">Try asking:</p>
          <div className="flex flex-wrap gap-2 justify-center">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => setInput(question)}
                className="px-4 py-2 bg-white border-2 border-blue-200 rounded-full text-sm hover:bg-blue-50 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-4 bg-white rounded-lg">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] p-4 rounded-2xl ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {message.role === 'assistant' && (
                <span className="text-2xl mr-2 float-left">🏒</span>
              )}
              {message.role === 'assistant' ? (
                <div className="hockey-iq-markdown">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      // Custom styling for markdown elements
                      p: ({children}) => <p className="mb-2 last:mb-0">{children}</p>,
                      ul: ({children}) => <ul className="list-disc list-inside mb-2 ml-2">{children}</ul>,
                      ol: ({children}) => <ol className="list-decimal list-inside mb-2 ml-2">{children}</ol>,
                      li: ({children}) => <li className="mb-1">{children}</li>,
                      strong: ({children}) => <strong className="font-bold text-gray-900">{children}</strong>,
                      em: ({children}) => <em className="italic">{children}</em>,
                      code: ({children}) => <code className="bg-gray-200 px-1 py-0.5 rounded text-sm">{children}</code>,
                      blockquote: ({children}) => (
                        <blockquote className="border-l-4 border-blue-300 pl-3 my-2 italic">{children}</blockquote>
                      ),
                      h1: ({children}) => <h1 className="text-xl font-bold mb-2">{children}</h1>,
                      h2: ({children}) => <h2 className="text-lg font-bold mb-2">{children}</h2>,
                      h3: ({children}) => <h3 className="text-base font-bold mb-1">{children}</h3>,
                      a: ({href, children}) => (
                        <a 
                          href={href} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 underline font-medium transition-colors duration-200"
                        >
                          {children}
                        </a>
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
              ) : (
                <span className="whitespace-pre-wrap">{message.content}</span>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 p-4 rounded-2xl">
              <div className="flex items-center gap-2">
                <span className="text-2xl">🏒</span>
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white rounded-lg shadow-lg p-4">
        {/* New Conversation Button */}
        {messages.length > 1 && (
          <button
            onClick={resetConversation}
            className="mb-2 text-sm text-gray-500 hover:text-gray-700 underline"
          >
            Start a new conversation
          </button>
        )}
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask me anything about hockey! 🏒"
            className="flex-1 px-4 py-3 text-lg border-2 border-gray-200 rounded-lg focus:border-blue-400 focus:outline-none"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={`px-6 py-3 rounded-lg font-bold text-lg transition-all transform hover:scale-105 ${
              input.trim() && !isLoading
                ? 'bg-blue-500 text-white hover:bg-blue-600 shadow-lg'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            Send! 🚀
          </button>
        </div>
        
        {selectedCategory && (
          <p className="text-xs text-gray-500 mt-2 text-center">
            Asking about: {selectedCategory.charAt(0).toUpperCase() + selectedCategory.slice(1).replace('_', ' ')}
          </p>
        )}
      </div>
    </div>
  )
})

KidFriendlyChat.displayName = 'KidFriendlyChat'