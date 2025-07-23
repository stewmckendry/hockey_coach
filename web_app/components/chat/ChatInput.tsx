'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'
import Button from '@/components/ui/Button'

interface ChatInputProps {
  onSendMessage: (message: string) => void
  isLoading: boolean
  disabled?: boolean
}

/**
 * Chat input component with send functionality
 */
export function ChatInput({ onSendMessage, isLoading, disabled = false }: ChatInputProps) {
  const [message, setMessage] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`
    }
  }, [message])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    const trimmedMessage = message.trim()
    if (!trimmedMessage || isLoading || disabled) return

    onSendMessage(trimmedMessage)
    setMessage('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const isMessageEmpty = !message.trim()

  return (
    <div className="border-t border-neutral-200 bg-white p-4">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
        <div className="flex items-end space-x-3">
          {/* Text Input */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about practice planning, player development, or hockey strategies..."
              disabled={disabled || isLoading}
              rows={1}
              className="w-full px-4 py-3 pr-12 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent outline-none resize-none transition-all duration-200 disabled:bg-neutral-50 disabled:text-neutral-500"
              style={{ minHeight: '48px', maxHeight: '120px' }}
            />
            
            {/* Character count (optional) */}
            {message.length > 100 && (
              <div className="absolute bottom-2 right-12 text-xs text-neutral-400">
                {message.length}
              </div>
            )}
          </div>

          {/* Send Button */}
          <Button
            type="submit"
            disabled={isMessageEmpty || isLoading || disabled}
            className="flex-shrink-0 h-12 w-12 p-0"
            aria-label="Send message"
          >
            {isLoading ? (
              <Loader2 size={20} className="animate-spin" />
            ) : (
              <Send size={20} />
            )}
          </Button>
        </div>

        {/* Quick suggestion buttons */}
        <div className="mt-3 flex flex-wrap gap-2">
          {quickSuggestions.map((suggestion, index) => (
            <button
              key={index}
              type="button"
              onClick={() => setMessage(suggestion.text)}
              disabled={disabled || isLoading}
              className="text-xs px-3 py-1 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-full transition-colors duration-200 disabled:opacity-50"
            >
              {suggestion.label}
            </button>
          ))}
        </div>

        {/* Help text */}
        <div className="mt-2 text-xs text-neutral-500 text-center">
          Press Enter to send, Shift+Enter for new line
        </div>
      </form>
    </div>
  )
}

// Quick suggestion prompts
const quickSuggestions = [
  {
    label: '🏒 Practice Plan',
    text: 'Create a 90-minute practice plan for U14 players focusing on passing and shooting'
  },
  {
    label: '📈 Player Development',
    text: 'Design a development plan for a forward to improve stickhandling skills'
  },
  {
    label: '🎯 Drill Search',
    text: 'Find drills for teaching defensive zone coverage'
  },
  {
    label: '💡 Coaching Tips',
    text: 'How do I help young players with confidence issues?'
  }
]

export default ChatInput
