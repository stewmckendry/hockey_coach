'use client'

import { HockeyIQInterface } from '@/components/hockey-iq/HockeyIQInterface'
import { useSearchParams } from 'next/navigation'
import { Suspense } from 'react'

function HockeyIQContent() {
  const searchParams = useSearchParams()
  const embedded = searchParams.get('embedded') === 'true'

  return (
    <div className={`min-h-screen ${embedded ? '' : 'bg-gradient-to-br from-blue-50 via-white to-blue-50'}`}>
      {!embedded && (
        <div className="max-w-6xl mx-auto p-4">
          <div className="text-center mb-6 pt-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">
              🏒 Hockey IQ Training Center
            </h1>
            <p className="text-lg text-gray-600">
              Learn hockey the fun way! Perfect for U10 players.
            </p>
          </div>
        </div>
      )}
      
      <div className={embedded ? 'h-screen' : 'max-w-6xl mx-auto p-4'}>
        <HockeyIQInterface 
          embedded={embedded}
          className={embedded ? 'h-full' : 'min-h-[600px] rounded-lg shadow-2xl'}
        />
      </div>

      {!embedded && (
        <footer className="mt-12 pb-8 text-center text-sm text-gray-500">
          <p>Made with ❤️ for young hockey players</p>
          <p className="mt-2">
            Embed in Notion: <code className="bg-gray-100 px-2 py-1 rounded">
              /hockey-iq?embedded=true
            </code>
          </p>
        </footer>
      )}
    </div>
  )
}

/**
 * Hockey IQ Chatbot Page
 * Can be accessed directly or embedded in Notion via iframe
 * URL: /hockey-iq
 * Embedded URL: /hockey-iq?embedded=true
 */
export default function HockeyIQPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">🏒</div>
          <div className="text-xl font-semibold text-gray-700">Loading Hockey IQ Coach...</div>
        </div>
      </div>
    }>
      <HockeyIQContent />
    </Suspense>
  )
}