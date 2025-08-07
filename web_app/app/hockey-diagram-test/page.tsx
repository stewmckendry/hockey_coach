'use client'

import { useState } from 'react'
import Image from 'next/image'
import { TechnicalDetails } from '@/components/hockey-diagram/TechnicalDetails'

interface DiagramResult {
  success: boolean
  imageBase64?: string
  processingTimeMs: number
  toolsUsed: string[]
  parserType?: string
  parserSpec?: any
  agentTraces?: any[]
  error?: string
  logId?: string
}

export default function HockeyDiagramTest() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DiagramResult | null>(null)
  const [showSpec, setShowSpec] = useState(false)
  const [showTraces, setShowTraces] = useState(false)
  
  // Feedback state
  const [rating, setRating] = useState(0)
  const [feedbackComment, setFeedbackComment] = useState('')
  const [feedbackCategories, setFeedbackCategories] = useState<string[]>([])
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)

  // Example prompts
  const examplePrompts = [
    "2-1-2 forecheck with F1 pressuring behind net",
    "Power play 1-3-1 umbrella formation",
    "Defensive zone coverage box plus one",
    "Neutral zone trap 1-3-1",
    "Breakout play strong side",
    "3v3 small area game in offensive zone",
    "Face-off setup for offensive zone draw",
    "Penalty kill diamond formation"
  ]

  const generateDiagram = async () => {
    if (!prompt.trim()) return

    setLoading(true)
    setResult(null)
    setFeedbackSubmitted(false)
    setRating(0)
    setFeedbackComment('')
    setFeedbackCategories([])

    try {
      const response = await fetch('/api/hockey-diagram/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (error) {
      console.error('Failed to generate diagram:', error)
      setResult({
        success: false,
        error: error instanceof Error ? error.message : 'Failed to generate diagram',
        processingTimeMs: 0,
        toolsUsed: []
      })
    } finally {
      setLoading(false)
    }
  }

  const submitFeedback = async () => {
    if (!result?.logId || rating === 0) return

    try {
      const response = await fetch('/api/hockey-diagram/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          logId: result.logId,
          rating,
          categories: feedbackCategories,
          comment: feedbackComment
        })
      })

      if (response.ok) {
        setFeedbackSubmitted(true)
      }
    } catch (error) {
      console.error('Failed to submit feedback:', error)
    }
  }

  const toggleCategory = (category: string) => {
    setFeedbackCategories(prev => 
      prev.includes(category) 
        ? prev.filter(c => c !== category)
        : [...prev, category]
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-4">
            <h1 className="text-2xl font-bold text-gray-900">🏒 Hockey Diagram Testing Console</h1>
            <p className="text-sm text-gray-500">Test and provide feedback on AI-generated hockey diagrams</p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <div>
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Generate Diagram</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Enter your hockey formation or drill description:
                  </label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="e.g., 2-1-2 forecheck with F1 pressuring behind net"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none"
                    rows={4}
                  />
                </div>

                <button
                  onClick={generateDiagram}
                  disabled={loading || !prompt.trim()}
                  className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Generating...
                    </>
                  ) : (
                    'Generate Diagram'
                  )}
                </button>
              </div>
            </div>

            {/* Example Prompts */}
            <div className="bg-white rounded-lg shadow p-6 mt-6">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Example Prompts</h3>
              <div className="space-y-2">
                {examplePrompts.map((example, index) => (
                  <button
                    key={index}
                    onClick={() => setPrompt(example)}
                    className="text-left w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded transition-colors"
                  >
                    • {example}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Output Section */}
          <div className="space-y-6">
            {result && (
              <>
                {/* Diagram Display */}
                <div className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-lg font-medium text-gray-900">Generated Diagram</h2>
                    <div className="text-sm text-gray-500">
                      {result.processingTimeMs}ms
                    </div>
                  </div>

                  {result.success && result.imageBase64 ? (
                    <div className="relative aspect-[4/3] bg-gray-100 rounded-lg overflow-hidden">
                      <img
                        src={`data:image/png;base64,${result.imageBase64}`}
                        alt="Hockey diagram"
                        className="w-full h-full object-contain"
                      />
                    </div>
                  ) : (
                    <div className="aspect-[4/3] bg-red-50 rounded-lg flex items-center justify-center">
                      <div className="text-center">
                        <p className="text-red-600 font-medium">Generation Failed</p>
                        <p className="text-sm text-red-500 mt-1">{result.error}</p>
                      </div>
                    </div>
                  )}

                  {/* Tool Chain */}
                  {result.toolsUsed.length > 0 && (
                    <div className="mt-4 p-3 bg-gray-50 rounded">
                      <p className="text-sm font-medium text-gray-700">Tool Chain:</p>
                      <p className="text-sm text-gray-600 mt-1">
                        {result.toolsUsed.join(' → ')}
                      </p>
                    </div>
                  )}
                </div>

                {/* Feedback Section */}
                {result.success && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Provide Feedback</h3>
                    
                    {!feedbackSubmitted ? (
                      <div className="space-y-4">
                        {/* Star Rating */}
                        <div>
                          <p className="text-sm font-medium text-gray-700 mb-2">Overall Rating</p>
                          <div className="flex gap-2">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <button
                                key={star}
                                onClick={() => setRating(star)}
                                className={`text-2xl transition-colors ${
                                  star <= rating ? 'text-yellow-400' : 'text-gray-300'
                                } hover:text-yellow-400`}
                              >
                                ★
                              </button>
                            ))}
                          </div>
                        </div>

                        {/* Categories */}
                        <div>
                          <p className="text-sm font-medium text-gray-700 mb-2">Feedback Categories</p>
                          <div className="flex flex-wrap gap-2">
                            {['Accuracy', 'Positioning', 'Clarity', 'Performance'].map((category) => (
                              <button
                                key={category}
                                onClick={() => toggleCategory(category)}
                                className={`px-3 py-1 rounded-full text-sm transition-colors ${
                                  feedbackCategories.includes(category)
                                    ? 'bg-blue-100 text-blue-700'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                }`}
                              >
                                {category}
                              </button>
                            ))}
                          </div>
                        </div>

                        {/* Comment */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Additional Comments
                          </label>
                          <textarea
                            value={feedbackComment}
                            onChange={(e) => setFeedbackComment(e.target.value)}
                            placeholder="What worked well? What could be improved?"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none"
                            rows={3}
                          />
                        </div>

                        <button
                          onClick={submitFeedback}
                          disabled={rating === 0}
                          className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                        >
                          Submit Feedback
                        </button>
                      </div>
                    ) : (
                      <div className="text-center py-4">
                        <p className="text-green-600 font-medium">✓ Thank you for your feedback!</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Technical Details */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Technical Details</h3>
                  <TechnicalDetails 
                    parserSpec={result.parserSpec}
                    agentTraces={result.agentTraces || []}
                  />
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}