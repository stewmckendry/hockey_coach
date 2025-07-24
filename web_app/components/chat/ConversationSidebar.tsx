import React from 'react'
import { formatTimestamp } from '@/lib/utils'
import type { ConversationThread } from '@/lib/types'

interface ConversationSidebarProps {
  conversations: ConversationThread[]
  activeConversationId: string | null
  onSelectConversation: (id: string) => void
  onNewConversation: () => void
  className?: string
}

export default function ConversationSidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  className = ''
}: ConversationSidebarProps) {
  return (
    <div className={`bg-neutral-50 border-r border-neutral-200 flex flex-col ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-neutral-200">
        <button
          onClick={onNewConversation}
          className="w-full bg-blue-600 text-white rounded-lg px-4 py-2 font-medium hover:bg-blue-700 transition-colors"
        >
          🏒 New Chat
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-neutral-500 text-sm">
            No conversations yet
          </div>
        ) : (
          conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`p-3 rounded-lg cursor-pointer transition-colors ${
                conversation.id === activeConversationId
                  ? 'bg-blue-600 text-white'
                  : 'hover:bg-neutral-100'
              }`}
              onClick={() => onSelectConversation(conversation.id)}
            >
              <h4 className="font-medium text-sm truncate">
                {conversation.title}
              </h4>
              <p className={`text-xs mt-1 ${
                conversation.id === activeConversationId 
                  ? 'text-blue-100' 
                  : 'text-neutral-500'
              }`}>
                {conversation.messages.length} messages • {formatTimestamp(conversation.updatedAt)}
              </p>
            </div>
          ))
        )}
      </div>

      {/* OpenAI State Info */}
      <div className="p-4 border-t border-neutral-200 text-xs text-neutral-500">
        <div className="flex items-center gap-2">
          <span>🤖</span>
          <span>Conversations managed by OpenAI Responses API</span>
        </div>
      </div>
    </div>
  )
}
