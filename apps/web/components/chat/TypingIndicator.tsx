'use client'

/**
 * Typing indicator component for chat
 */
export function TypingIndicator() {
  return (
    <div className="flex justify-start w-full mb-4">
      <div className="flex max-w-[80%] md:max-w-[70%]">
        {/* AI Avatar */}
        <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium bg-neutral-200 text-neutral-700 mr-3">
          🏒
        </div>

        {/* Typing Animation */}
        <div className="bg-white text-neutral-900 border border-neutral-200 rounded-2xl rounded-bl-md shadow-sm px-4 py-3">
          <div className="flex items-center space-x-1">
            <span className="text-sm text-neutral-600">AI is thinking</span>
            <div className="flex space-x-1 ml-2">
              <div className="w-2 h-2 bg-hockey-blue rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-hockey-blue rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-hockey-blue rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TypingIndicator
