'use client'

import { cn } from '@/lib/utils'
import type { LoadingSpinnerProps } from '@/lib/types'

/**
 * Loading spinner with hockey theming
 */
export function LoadingSpinner({ size = 'md', className }: LoadingSpinnerProps) {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  }

  return (
    <div className={cn('flex items-center justify-center', className)}>
      <div
        className={cn(
          'animate-spin rounded-full border-2 border-hockey-blue border-t-transparent',
          sizes[size]
        )}
        role="status"
        aria-label="Loading"
      >
        <span className="sr-only">Loading...</span>
      </div>
    </div>
  )
}

/**
 * Typing indicator for chat
 */
export function TypingIndicator() {
  return (
    <div className="flex items-center space-x-1 text-neutral-500">
      <span className="text-sm">AI is thinking</span>
      <div className="flex space-x-1">
        <div className="w-1 h-1 bg-current rounded-full animate-pulse"></div>
        <div className="w-1 h-1 bg-current rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
        <div className="w-1 h-1 bg-current rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
      </div>
    </div>
  )
}

export default LoadingSpinner
