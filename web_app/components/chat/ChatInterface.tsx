'use client'

import { useChat } from '@/hooks/useChat'
import { MessageBubble } from './MessageBubble'
import { ChatInput } from './ChatInput'
import { TypingIndicator } from './TypingIndicator'
import { useEffect, useRef } from 'react'
import { ChatMessage } from '@/lib/types'

interface ChatInterfaceProps {
  className?: string
}

/**
 * Main chat interface component that manages the conversation flow
 */
export function ChatInterface({ className = '' }: ChatInterfaceProps) {
  const { messages, isLoading, sendMessage, error } = useChat()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  const handleSendMessage = async (content: string) => {
    await sendMessage(content)
  }

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Chat Messages Container */}
      <div 
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto scroll-smooth px-4 py-6 space-y-4"
      >
        {/* Welcome Message */}
        {messages.length === 0 && (
          <div className="flex justify-center items-center h-32">
            <div className="text-center text-neutral-500 max-w-md">
              <div className="text-4xl mb-4">🏒</div>
              <h3 className="text-lg font-medium text-neutral-700 mb-2">
                Welcome to Your Hockey Coaching Assistant
              </h3>
              <p className="text-sm">
                Ask me anything about hockey skills, practice planning, player development, or game tactics. 
                I'm here to help you become a better coach!
              </p>
            </div>
          </div>
        )}

        {/* Chat Messages */}
        {messages.map((message: ChatMessage) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {/* Typing Indicator */}
        {isLoading && <TypingIndicator />}

        {/* Error Message */}
        {error && (
          <div className="flex justify-center">
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg max-w-md text-center">
              <p className="text-sm font-medium">Something went wrong</p>
              <p className="text-xs mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <div className="border-t border-neutral-200 bg-white px-4 py-4">
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isLoading}
          placeholder="Ask about hockey skills, drills, tactics, or player development..."
        />
      </div>
    </div>
  )
}

export default ChatInterface
