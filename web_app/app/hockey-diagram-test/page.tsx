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

interface ModificationEntry {
  feedback: string
  changes: Array<{
    type: string
    target: string
    details: string
  }>
  explanation: string
  timestamp: Date
}

export default function HockeyDiagramTest() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DiagramResult | null>(null)
  const [showSpec, setShowSpec] = useState(false)
  const [showTraces, setShowTraces] = useState(false)
  
  // Interactive editing state
  const [currentSpec, setCurrentSpec] = useState<any>(null)
  const [feedbackMode, setFeedbackMode] = useState(false)
  const [modificationText, setModificationText] = useState('')
  const [modificationHistory, setModificationHistory] = useState<ModificationEntry[]>([])
  const [isProcessingFeedback, setIsProcessingFeedback] = useState(false)
  
  // Cache state
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [savedDiagramId, setSavedDiagramId] = useState<string | null>(null)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [showLibrary, setShowLibrary] = useState(false)
  const [libraryDiagrams, setLibraryDiagrams] = useState<any[]>([])
  const [loadingLibrary, setLoadingLibrary] = useState(false)
  const [libraryTotal, setLibraryTotal] = useState(0)
  const [libraryOffset, setLibraryOffset] = useState(0)
  const [libraryHasMore, setLibraryHasMore] = useState(false)

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
    setSaved(false)
    setSavedDiagramId(null)
    setSaveError(null)
    setModificationHistory([])
    setFeedbackMode(false)
    setModificationText('')

    try {
      console.log('🚀 Generating diagram for prompt:', prompt)
      
      const response = await fetch('/api/hockey-diagram/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt })
      })

      console.log('📡 Response status:', response.status)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ HTTP error:', response.status, errorText)
        throw new Error(`HTTP error! status: ${response.status}: ${errorText}`)
      }

      const data = await response.json()
      console.log('📦 Response data:', {
        success: data.success,
        hasImageBase64: !!data.imageBase64,
        imageBase64Length: data.imageBase64?.length || 0,
        toolsUsed: data.toolsUsed,
        parserType: data.parserType,
        error: data.error,
        processingTimeMs: data.processingTimeMs,
        agentTracesCount: data.agentTraces?.length || 0,
        agentTraces: data.agentTraces
      })
      
      // Log the first 100 chars of base64 if present
      if (data.imageBase64) {
        console.log('🖼️ Image base64 preview:', data.imageBase64.substring(0, 100) + '...')
      }
      
      setResult(data)
      // Store the spec for interactive editing
      // First try to extract from agentTraces (most accurate)
      let actualSpec = null
      if (data.agentTraces && data.agentTraces.length > 0) {
        // Look for the generate_diagram_from_spec tool call which has the zone-based spec in its arguments
        // The spec passed to generate_diagram_from_spec has zones, which get converted to coordinates internally
        for (const trace of data.agentTraces) {
          if (trace.name === 'generate_diagram_from_spec') {
            try {
              const args = typeof trace.arguments === 'string' ? JSON.parse(trace.arguments) : trace.arguments
              if (args.diagram_spec) {
                // The diagram_spec argument contains the zone-based spec
                actualSpec = typeof args.diagram_spec === 'string' ? JSON.parse(args.diagram_spec) : args.diagram_spec
                console.log('✅ Extracted zone-based spec from generate_diagram_from_spec arguments:', actualSpec)
                console.log('Spec keys:', Object.keys(actualSpec))
                if (actualSpec.players && actualSpec.players.length > 0) {
                  console.log('First player:', actualSpec.players[0])
                }
                break
              }
            } catch (e) {
              console.warn('Failed to parse spec from generate trace:', e)
            }
          }
        }
      }
      
      // Fallback to parserSpec if it's an object with players array
      if (!actualSpec && data.parserSpec && typeof data.parserSpec === 'object' && data.parserSpec.players) {
        actualSpec = data.parserSpec
        console.log('✅ Using parserSpec as it has players array')
      }
      
      if (actualSpec) {
        setCurrentSpec(actualSpec)
        console.log('📋 Set currentSpec with', Object.keys(actualSpec))
      } else {
        console.warn('⚠️ Could not extract diagram spec for interactive editing')
      }
    } catch (error) {
      console.error('❌ Failed to generate diagram:', error)
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

  // Save diagram to cache
  const saveDiagram = async () => {
    if (!prompt) {
      console.error('❌ Cannot save: Missing prompt')
      return
    }

    // Extract the actual spec from traces or parserSpec
    let actualSpec = null
    
    // First try to extract from agentTraces (most accurate)
    if (result?.agentTraces && result.agentTraces.length > 0) {
      // Look for the generate_diagram_from_spec tool call which has the full spec
      for (const trace of result.agentTraces) {
        if (trace.name === 'generate_diagram_from_spec') {
          try {
            const args = typeof trace.arguments === 'string' ? JSON.parse(trace.arguments) : trace.arguments
            if (args.diagram_spec) {
              actualSpec = typeof args.diagram_spec === 'string' ? JSON.parse(args.diagram_spec) : args.diagram_spec
              console.log('✅ Extracted spec from generate_diagram_from_spec trace')
              break
            }
          } catch (e) {
            console.warn('Failed to parse spec from trace:', e)
          }
        }
      }
    }
    
    // Fallback to parserSpec if it's an object (not the RunResult string)
    if (!actualSpec && result?.parserSpec && typeof result.parserSpec === 'object') {
      actualSpec = result.parserSpec
      console.log('✅ Using parserSpec as it is already an object')
    }
    
    if (!actualSpec) {
      console.error('❌ Cannot save: Could not extract diagram specification', {
        hasAgentTraces: !!(result?.agentTraces?.length),
        parserSpecType: typeof result?.parserSpec
      })
      return
    }

    setSaving(true)
    console.log('💾 Saving diagram to cache...', {
      prompt,
      spec: actualSpec,
      parserType: result?.parserType
    })
    
    try {
      const response = await fetch('/api/hockey-diagram/cache', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          action: 'save',
          data: {
            prompt,
            spec: actualSpec,
            parserType: result?.parserType || 'unknown',
            tags: ['test', 'web-ui'],
            author: 'web-user'
          }
        })
      })

      console.log('📡 Save response status:', response.status)
      const data = await response.json()
      console.log('📦 Save response data:', data)
      
      if (data.success) {
        setSaved(true)
        setSavedDiagramId(data.diagram_id)
        setSaveError(null)
        console.log('✅ Diagram saved with ID:', data.diagram_id)
        setTimeout(() => {
          setSaved(false)
          setSavedDiagramId(null)
        }, 5000) // Reset after 5 seconds
      } else {
        setSaveError(data.error || 'Failed to save diagram')
        console.error('❌ Save failed:', data.error)
        setTimeout(() => setSaveError(null), 5000) // Clear error after 5 seconds
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to save diagram'
      setSaveError(errorMsg)
      console.error('❌ Failed to save diagram:', error)
      setTimeout(() => setSaveError(null), 5000) // Clear error after 5 seconds
    } finally {
      setSaving(false)
    }
  }

  // Load library of cached diagrams with pagination
  const loadLibrary = async (offset: number = 0) => {
    setLoadingLibrary(true)
    console.log(`📚 Loading diagram library (offset: ${offset})...`)
    
    try {
      // Use the new list endpoint to get all diagrams
      const response = await fetch(`/api/hockey-diagram/cache?action=list&limit=20&offset=${offset}&sortBy=created_at`)
      console.log('📡 Library response status:', response.status)
      
      const data = await response.json()
      console.log('📦 Library data:', data)
      
      if (data.success && data.diagrams) {
        setLibraryDiagrams(data.diagrams)
        setLibraryTotal(data.total || 0)
        setLibraryOffset(data.offset || 0)
        setLibraryHasMore(data.has_more || false)
        console.log(`✅ Loaded ${data.diagrams.length} diagrams (${data.total} total)`)
        
        if (data.has_more) {
          console.log(`📄 More diagrams available (showing ${data.offset + 1}-${data.offset + data.diagrams.length} of ${data.total})`)
        }
      } else if (!data.success) {
        console.error('❌ Failed to load library:', data.error)
        setLibraryDiagrams([])
        setLibraryTotal(0)
        setLibraryHasMore(false)
      } else {
        console.log('📭 No diagrams in library')
        setLibraryDiagrams([])
        setLibraryTotal(0)
        setLibraryHasMore(false)
      }
    } catch (error) {
      console.error('❌ Failed to load library:', error)
      setLibraryDiagrams([])
      setLibraryTotal(0)
      setLibraryHasMore(false)
    } finally {
      setLoadingLibrary(false)
    }
  }

  // Load a cached diagram
  const loadCachedDiagram = async (diagramId: string, diagramPrompt: string) => {
    setLoading(true)
    try {
      const response = await fetch(`/api/hockey-diagram/cache?action=get&id=${diagramId}&regenerate=true`)
      const data = await response.json()
      
      if (data.success && data.diagram) {
        setPrompt(diagramPrompt)
        setResult({
          success: true,
          imageBase64: data.image_base64,
          processingTimeMs: 0,
          toolsUsed: ['cached'],
          parserType: data.diagram.parser_type,
          parserSpec: data.diagram.spec
        })
        setShowLibrary(false)
      }
    } catch (error) {
      console.error('Failed to load cached diagram:', error)
    } finally {
      setLoading(false)
    }
  }

  // Toggle library view
  const toggleLibrary = () => {
    setShowLibrary(!showLibrary)
    if (!showLibrary && libraryDiagrams.length === 0) {
      loadLibrary(0)  // Start from the beginning
    }
  }

  // Process modification feedback
  const processFeedback = async () => {
    if (!modificationText.trim() || !currentSpec) return

    setIsProcessingFeedback(true)
    
    try {
      const response = await fetch('/api/hockey-diagram/feedback-processor', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          currentSpec,
          feedback: modificationText
        })
      })

      if (!response.ok) {
        throw new Error(`Failed to process feedback: ${response.status}`)
      }

      const data = await response.json()
      
      if (data.success) {
        // Update the spec
        setCurrentSpec(data.updatedSpec)
        
        // Add to modification history
        setModificationHistory([
          ...modificationHistory,
          {
            feedback: modificationText,
            changes: data.changes || [],
            explanation: data.explanation || 'Changes applied',
            timestamp: new Date()
          }
        ])
        
        // Generate new diagram from updated spec
        const genResponse = await fetch('/api/hockey-diagram/generate-from-spec', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            spec: data.updatedSpec
          })
        })
        
        if (genResponse.ok) {
          const genData = await genResponse.json()
          setResult({
            ...result!,
            imageBase64: genData.imageBase64,
            parserSpec: data.updatedSpec
          })
        }
        
        // Clear input and exit feedback mode
        setModificationText('')
        setFeedbackMode(false)
      } else {
        console.error('Feedback processing failed:', data.error)
        alert(`Failed to process feedback: ${data.error}`)
      }
    } catch (error) {
      console.error('Error processing feedback:', error)
      alert('Failed to process feedback. Please try again.')
    } finally {
      setIsProcessingFeedback(false)
    }
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

                <div className="flex gap-2">
                  <button
                    onClick={generateDiagram}
                    disabled={loading || !prompt.trim()}
                    className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
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
                  
                  <button
                    onClick={toggleLibrary}
                    className="px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    📚 Library
                  </button>
                </div>
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
                    <div className="flex items-center gap-3">
                      <div className="text-sm text-gray-500">
                        {result.processingTimeMs}ms
                      </div>
                      {result.success && (
                        <button
                          onClick={saveDiagram}
                          disabled={saving || saved}
                          className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                            saved 
                              ? 'bg-green-100 text-green-700' 
                              : saveError
                              ? 'bg-red-100 text-red-700'
                              : saving
                              ? 'bg-gray-100 text-gray-500'
                              : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                          }`}
                        >
                          {saved ? '✓ Saved' : saveError ? '✗ Failed' : saving ? 'Saving...' : '💾 Save'}
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Save status notification */}
                  {(saved || saveError) && (
                    <div className={`mb-4 p-3 rounded-lg text-sm ${
                      saved 
                        ? 'bg-green-50 border border-green-200 text-green-800'
                        : 'bg-red-50 border border-red-200 text-red-800'
                    }`}>
                      {saved ? (
                        <div>
                          <strong>✓ Diagram saved successfully!</strong>
                          {savedDiagramId && (
                            <span className="ml-2 text-xs text-green-600">
                              ID: {savedDiagramId}
                            </span>
                          )}
                        </div>
                      ) : (
                        <div>
                          <strong>✗ Failed to save diagram</strong>
                          {saveError && (
                            <span className="ml-2 text-xs">
                              {saveError}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                  {result.success && result.imageBase64 ? (
                    <div className="relative aspect-[4/3] bg-gray-100 rounded-lg overflow-hidden">
                      <img
                        src={result.imageBase64.startsWith('data:') ? result.imageBase64 : `data:image/png;base64,${result.imageBase64}`}
                        alt="Hockey diagram"
                        className="w-full h-full object-contain"
                        onError={(e) => {
                          console.error('❌ Image failed to load:', e)
                          console.log('Image src:', (e.target as HTMLImageElement).src.substring(0, 100))
                        }}
                        onLoad={() => {
                          console.log('✅ Image loaded successfully')
                        }}
                      />
                    </div>
                  ) : (
                    <div className="aspect-[4/3] bg-red-50 rounded-lg flex items-center justify-center">
                      <div className="text-center">
                        <p className="text-red-600 font-medium">Generation Failed</p>
                        <p className="text-sm text-red-500 mt-1">{result.error || 'No image data received'}</p>
                        {!result.success && (
                          <p className="text-xs text-gray-500 mt-2">
                            Debug: success={String(result.success)}, hasImage={String(!!result.imageBase64)}
                          </p>
                        )}
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
                  
                  {/* Interactive Editing Button */}
                  {result.success && currentSpec && !feedbackMode && (
                    <div className="mt-4">
                      <button
                        onClick={() => setFeedbackMode(true)}
                        className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                      >
                        ✏️ Modify Diagram
                      </button>
                    </div>
                  )}
                  
                  {/* Feedback Mode UI */}
                  {feedbackMode && (
                    <div className="mt-4 p-4 bg-purple-50 rounded-lg border border-purple-200">
                      <h4 className="text-sm font-medium text-purple-900 mb-2">
                        Describe what you want to change:
                      </h4>
                      <textarea
                        value={modificationText}
                        onChange={(e) => setModificationText(e.target.value)}
                        placeholder="e.g., Move F1 to the slot, Add passing lanes between defensemen"
                        className="w-full px-3 py-2 border border-purple-300 rounded focus:ring-2 focus:ring-purple-500 focus:outline-none resize-none"
                        rows={3}
                        disabled={isProcessingFeedback}
                      />
                      <div className="flex gap-2 mt-3">
                        <button
                          onClick={processFeedback}
                          disabled={isProcessingFeedback || !modificationText.trim()}
                          className="flex-1 px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                        >
                          {isProcessingFeedback ? 'Processing...' : 'Apply Changes'}
                        </button>
                        <button
                          onClick={() => {
                            setFeedbackMode(false)
                            setModificationText('')
                          }}
                          disabled={isProcessingFeedback}
                          className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                  
                  {/* Modification History */}
                  {modificationHistory.length > 0 && (
                    <div className="mt-4 p-3 bg-blue-50 rounded">
                      <p className="text-sm font-medium text-blue-900 mb-2">
                        Modification History ({modificationHistory.length})
                      </p>
                      <div className="space-y-2">
                        {modificationHistory.map((mod, index) => (
                          <div key={index} className="text-sm">
                            <div className="font-medium text-blue-800">
                              {index + 1}. "{mod.feedback}"
                            </div>
                            <div className="text-blue-600 ml-4">
                              → {mod.explanation}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>


                {/* Technical Details */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Technical Details</h3>
                  <TechnicalDetails 
                    parserSpec={currentSpec || result.parserSpec}
                    agentTraces={result.agentTraces || []}
                  />
                </div>
              </>
            )}
          </div>
        </div>
      </div>
      
      {/* Library Modal */}
      {showLibrary && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <div className="border-b px-6 py-4 flex justify-between items-center">
              <h2 className="text-xl font-semibold">Diagram Library</h2>
              <button
                onClick={() => setShowLibrary(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="overflow-y-auto max-h-[calc(80vh-120px)] p-6">
              {loadingLibrary ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="mt-2 text-gray-500">Loading diagrams...</p>
                </div>
              ) : libraryDiagrams.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No saved diagrams yet. Generate and save a diagram to start your library!
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {libraryDiagrams.map((diagram) => (
                    <div
                      key={diagram.id}
                      className="border rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer"
                      onClick={() => loadCachedDiagram(diagram.id, diagram.prompt)}
                    >
                      <h3 className="font-medium text-gray-900 mb-2 line-clamp-2">
                        {diagram.prompt}
                      </h3>
                      <div className="flex justify-between text-sm text-gray-500">
                        <span>Parser: {diagram.parser_type}</span>
                        <span>Uses: {diagram.usage_count}</span>
                      </div>
                      <div className="mt-2 flex gap-2">
                        {diagram.validated && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            ✓ Validated
                          </span>
                        )}
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          Similarity: {(diagram.similarity * 100).toFixed(0)}%
                        </span>
                      </div>
                      {diagram.tags && diagram.tags.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {diagram.tags.map((tag: string, idx: number) => (
                            <span
                              key={idx}
                              className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            <div className="border-t px-6 py-3 flex justify-between items-center">
              <div className="text-sm text-gray-500">
                {libraryTotal > 0 && (
                  <>
                    Showing {libraryOffset + 1}-{Math.min(libraryOffset + libraryDiagrams.length, libraryTotal)} of {libraryTotal} diagrams
                  </>
                )}
                {libraryTotal === 0 && 'No diagrams in library'}
              </div>
              <div className="flex gap-2">
                {libraryOffset > 0 && (
                  <button
                    onClick={() => loadLibrary(Math.max(0, libraryOffset - 20))}
                    className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
                  >
                    ← Previous
                  </button>
                )}
                {libraryHasMore && (
                  <button
                    onClick={() => loadLibrary(libraryOffset + 20)}
                    className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
                  >
                    Next →
                  </button>
                )}
                <button
                  onClick={() => loadLibrary(0)}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                >
                  Refresh
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}