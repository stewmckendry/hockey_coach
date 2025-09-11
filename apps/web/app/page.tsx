'use client'

import ChatInterface from '@/components/chat/ChatInterface'

export default function HomePage() {
  return (
    <div className="flex-1 flex flex-col">
      {/* Hero Section */}
      <div className="bg-hockey-gradient text-white py-8 md:py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            🏒 Hockey Coach AI Assistant
          </h1>
          <p className="text-lg md:text-xl text-hockey-ice opacity-90 max-w-2xl mx-auto">
            Your intelligent partner for season planning, practice design, and player development. 
            Ask anything about hockey coaching strategies.
          </p>
        </div>
      </div>

      {/* Chat Interface */}
      <div className="flex-1 flex flex-col">
        <ChatInterface />
      </div>

      {/* Quick Start Cards */}
      <div className="bg-neutral-50 border-t border-neutral-200 py-6">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4 text-center">
            Quick Start Examples
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="card">
              <h4 className="font-medium text-hockey-blue mb-2">🎯 Practice Planning</h4>
              <p className="text-sm text-neutral-600">
                "Create a 90-minute practice for U14 focusing on power play systems"
              </p>
            </div>
            <div className="card">
              <h4 className="font-medium text-hockey-blue mb-2">📈 Player Development</h4>
              <p className="text-sm text-neutral-600">
                "Design a 6-week development plan for a defenseman to improve puck handling"
              </p>
            </div>
            <div className="card">
              <h4 className="font-medium text-hockey-blue mb-2">🔍 Knowledge Search</h4>
              <p className="text-sm text-neutral-600">
                "Find drills for teaching backchecking to forwards"
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
