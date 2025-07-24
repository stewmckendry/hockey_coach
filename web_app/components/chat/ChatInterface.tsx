'use client'

import { useChat } from '@/hooks/useChat'
import { MessageBubble } from './MessageBubble'
import { ChatInput } from './ChatInput'
import { TypingIndicator } from './TypingIndicator'
import ConversationSidebar from './ConversationSidebar'
import { useEffect, useRef, useState } from 'react'
import { ChatMessage } from '@/lib/types'

interface ChatInterfaceProps {
  className?: string
  showSidebar?: boolean
}

/**
 * Main chat interface component with OpenAI Responses API conversation management
 */
export function ChatInterface({ className = '', showSidebar = false }: ChatInterfaceProps) {
  const {
    messages,
    conversations,
    activeConversationId,
    createNewConversation,
    selectConversation,
    sendMessage,
    isLoading,
    error
  } = useChat()
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false) // Hidden by default, can be toggled

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
    <div className={`flex h-full ${className}`}>
      {/* Conversation Sidebar */}
      {sidebarOpen && (
        <div className="w-80 border-r border-neutral-200 bg-neutral-50">
          <ConversationSidebar
            conversations={conversations}
            activeConversationId={activeConversationId}
            onSelectConversation={selectConversation}
            onNewConversation={createNewConversation}
            className="h-full"
          />
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-neutral-200 bg-white">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-neutral-100 rounded transition-colors"
              title="Toggle conversation list"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div>
              <h1 className="text-lg font-semibold text-neutral-900">🏒 Hockey Coach Assistant</h1>
              {activeConversationId && (
                <p className="text-xs text-neutral-500">
                  Powered by OpenAI Responses API • Context-aware conversations
                </p>
              )}
            </div>
          </div>
          
          <button
            onClick={createNewConversation}
            className="text-sm px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            title="Start a new conversation"
          >
            New Chat
          </button>
        </div>

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
                <p className="text-sm mb-4">
                  Ask me anything about hockey skills, practice planning, player development, or game tactics. 
                  I'm here to help you become a better coach!
                </p>
                {!activeConversationId && (
                  <div className="text-xs text-neutral-400 bg-neutral-50 rounded-lg p-3">
                    <p className="font-medium mb-1">🤖 Enhanced with OpenAI Responses API</p>
                    <p>I remember our entire conversation context automatically</p>
                  </div>
                )}
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
                <button
                  onClick={() => window.location.reload()}
                  className="text-xs underline mt-2 hover:no-underline"
                >
                  Try refreshing the page
                </button>
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
            isLoading={isLoading}
            disabled={isLoading}
          />
          
          {/* Context indicator */}
          {activeConversationId && messages.length > 0 && (
            <div className="mt-2 text-xs text-neutral-500 flex items-center gap-2">
              <span className="w-2 h-2 bg-green-400 rounded-full"></span>
              <span>Conversation context maintained by OpenAI</span>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50 bg-black bg-opacity-50" onClick={() => setSidebarOpen(false)}>
          <div className="w-80 h-full bg-white" onClick={(e) => e.stopPropagation()}>
            <ConversationSidebar
              conversations={conversations}
              activeConversationId={activeConversationId}
              onSelectConversation={(id) => {
                selectConversation(id)
                setSidebarOpen(false)
              }}
              onNewConversation={() => {
                createNewConversation()
                setSidebarOpen(false)
              }}
              className="h-full"
            />
          </div>
        </div>
      )}
    </div>
  )
}

export default ChatInterface
