'use client'

import { formatTimestamp, cn } from '@/lib/utils'
import type { ChatMessage } from '@/lib/types'

interface MessageBubbleProps {
  message: ChatMessage
}

/**
 * Individual message bubble component
 */
export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div className={cn(
      'flex w-full mb-4',
      isUser ? 'justify-end' : 'justify-start'
    )}>
      <div className={cn(
        'flex max-w-[80%] md:max-w-[70%]',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}>
        {/* Avatar */}
        <div className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
          isUser 
            ? 'bg-hockey-blue text-white ml-3' 
            : 'bg-neutral-200 text-neutral-700 mr-3'
        )}>
          {isUser ? '👤' : '🏒'}
        </div>

        {/* Message Content */}
        <div className="flex flex-col">
          {/* Message Bubble */}
          <div className={cn(
            'px-4 py-3 rounded-2xl',
            isUser 
              ? 'bg-hockey-blue text-white rounded-br-md' 
              : 'bg-white text-neutral-900 border border-neutral-200 rounded-bl-md shadow-sm'
          )}>
            <div className="prose prose-sm max-w-none">
              <MessageContent content={message.content} />
            </div>
          </div>

          {/* Timestamp and Metadata */}
          <div className={cn(
            'flex items-center mt-1 text-xs text-neutral-500',
            isUser ? 'justify-end' : 'justify-start'
          )}>
            <span>{formatTimestamp(message.timestamp)}</span>
            {message.metadata?.processingTime && (
              <span className="ml-2">
                • {Math.round(message.metadata.processingTime / 1000 * 10) / 10}s
              </span>
            )}
            {message.metadata?.error && (
              <span className="ml-2 text-hockey-red">
                • Error
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * Render message content with basic markdown support
 */
function MessageContent({ content }: { content: string }) {
  // Simple markdown parsing for chat messages
  const lines = content.split('\n')
  
  return (
    <div className="space-y-2">
      {lines.map((line, index) => {
        // Headers
        if (line.startsWith('# ')) {
          return (
            <h3 key={index} className="text-lg font-bold mt-4 mb-2 first:mt-0">
              {line.substring(2)}
            </h3>
          )
        }
        
        if (line.startsWith('## ')) {
          return (
            <h4 key={index} className="text-base font-semibold mt-3 mb-2 first:mt-0">
              {line.substring(3)}
            </h4>
          )
        }
        
        if (line.startsWith('### ')) {
          return (
            <h5 key={index} className="text-sm font-semibold mt-2 mb-1 first:mt-0">
              {line.substring(4)}
            </h5>
          )
        }

        // Bold text
        if (line.startsWith('**') && line.endsWith('**')) {
          return (
            <p key={index} className="font-semibold">
              {line.substring(2, line.length - 2)}
            </p>
          )
        }

        // Lists
        if (line.startsWith('- ')) {
          return (
            <div key={index} className="flex items-start space-x-2">
              <span className="text-hockey-blue mt-1">•</span>
              <span>{line.substring(2)}</span>
            </div>
          )
        }

        // Regular paragraphs
        if (line.trim()) {
          return (
            <p key={index} className="leading-relaxed">
              {formatInlineMarkdown(line)}
            </p>
          )
        }

        // Empty lines for spacing
        return <div key={index} className="h-2" />
      })}
    </div>
  )
}

/**
 * Format inline markdown like **bold** and *italic*
 */
function formatInlineMarkdown(text: string) {
  // This is a simple implementation - in production you might want to use a proper markdown library
  const parts = []
  let current = text
  let key = 0

  while (current.length > 0) {
    // Bold text **text**
    const boldMatch = current.match(/\*\*(.*?)\*\*/)
    if (boldMatch) {
      const beforeBold = current.substring(0, boldMatch.index)
      if (beforeBold) {
        parts.push(<span key={key++}>{beforeBold}</span>)
      }
      parts.push(<strong key={key++}>{boldMatch[1]}</strong>)
      current = current.substring(boldMatch.index! + boldMatch[0].length)
      continue
    }

    // Italic text *text*
    const italicMatch = current.match(/\*(.*?)\*/)
    if (italicMatch) {
      const beforeItalic = current.substring(0, italicMatch.index)
      if (beforeItalic) {
        parts.push(<span key={key++}>{beforeItalic}</span>)
      }
      parts.push(<em key={key++}>{italicMatch[1]}</em>)
      current = current.substring(italicMatch.index! + italicMatch[0].length)
      continue
    }

    // No more formatting, add the rest
    parts.push(<span key={key++}>{current}</span>)
    break
  }

  return parts.length > 1 ? parts : text
}

export default MessageBubble
