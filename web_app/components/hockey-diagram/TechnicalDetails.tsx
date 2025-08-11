import React from 'react'

interface ParsedSpec {
  diagram_type?: string
  title?: string
  view?: string
  players?: Array<{
    position: string
    zone: string
    team: string
    has_puck?: boolean
    x?: number
    y?: number
  }>
  movements?: any[]
}

interface AgentTrace {
  name: string
  arguments: string
  order: number
  output: string
}

interface TechnicalDetailsProps {
  parserSpec: any
  agentTraces: AgentTrace[]
}

export function TechnicalDetails({ parserSpec, agentTraces }: TechnicalDetailsProps) {
  // Debug logging
  console.log('TechnicalDetails received:', { parserSpec, agentTraces })
  
  // Extract the meaningful message from RunResult format
  const extractMessage = (spec: any) => {
    if (!spec) return null
    
    // If it's already a structured object with diagram info
    if (typeof spec === 'object' && !Array.isArray(spec)) {
      if (spec.title || spec.diagram_type) {
        return {
          status: `Generated ${spec.diagram_type || 'diagram'}: ${spec.title || 'Untitled'}`,
          description: spec.description || `View: ${spec.view || 'full_rink'}, Players: ${spec.players?.length || 0}`
        }
      }
    }
    
    const specStr = typeof spec === 'string' ? spec : JSON.stringify(spec)
    
    // Extract the message between ✅ and 📁
    const messageMatch = specStr.match(/✅\s*(.*?)\s*📁/s)
    const formationMatch = specStr.match(/🏒\s*Formation:\s*(.*?)(?:\n|```|$)/s)
    
    return {
      status: messageMatch?.[1]?.trim() || 'Diagram generated',
      description: formationMatch?.[1]?.trim() || ''
    }
  }

  // Parse tool arguments and output
  const parseToolData = (trace: AgentTrace) => {
    try {
      // Handle case where arguments and output might be strings or already objects
      let args = trace.arguments
      let output = trace.output
      
      // Parse arguments if it's a JSON string
      if (typeof args === 'string') {
        if (args.trim().startsWith('{') || args.trim().startsWith('[')) {
          try {
            args = JSON.parse(args)
          } catch (e) {
            // Keep as string if parsing fails
          }
        }
      }
      
      // Parse output if it's a JSON string (but might be truncated)
      if (typeof output === 'string') {
        // Check if it looks like truncated JSON (ends with ...)
        if (output.includes('...') && output.lastIndexOf('...') > output.length - 10) {
          // It's truncated, try to parse what we have
          const cleanOutput = output.substring(0, output.lastIndexOf('...'))
          if (cleanOutput.trim().startsWith('{') || cleanOutput.trim().startsWith('[')) {
            try {
              // Try to add closing brackets to make it valid JSON
              let testJson = cleanOutput
              const openBraces = (cleanOutput.match(/{/g) || []).length
              const closeBraces = (cleanOutput.match(/}/g) || []).length
              const openBrackets = (cleanOutput.match(/\[/g) || []).length
              const closeBrackets = (cleanOutput.match(/\]/g) || []).length
              
              // Add missing closing brackets/braces
              testJson += ']'.repeat(Math.max(0, openBrackets - closeBrackets))
              testJson += '}'.repeat(Math.max(0, openBraces - closeBraces))
              
              output = JSON.parse(testJson)
              output._truncated = true
            } catch (e) {
              // Keep as truncated string
              output = { _raw: cleanOutput, _truncated: true }
            }
          }
        } else if (output.trim().startsWith('{') || output.trim().startsWith('[')) {
          try {
            output = JSON.parse(output)
          } catch (e) {
            // Keep as string if parsing fails
          }
        }
      }
        
      return { args, output }
    } catch (e) {
      console.warn('Failed to parse trace data:', e)
      return { args: trace.arguments || 'N/A', output: trace.output || 'N/A' }
    }
  }

  // Format tool-specific display
  const renderToolDetails = (trace: AgentTrace) => {
    const { args, output } = parseToolData(trace)
    
    if (trace.name === 'parse_hockey_formation') {
      return (
        <div className="space-y-2">
          <div>
            <span className="font-medium text-gray-600">Input:</span>
            <div className="text-sm text-gray-800 mt-1">
              {typeof args === 'object' ? (
                <pre className="bg-gray-50 p-2 rounded overflow-x-auto whitespace-pre-wrap">
                  {JSON.stringify(args, null, 2)}
                </pre>
              ) : (
                <p>{args || 'N/A'}</p>
              )}
            </div>
          </div>
          {output && typeof output === 'object' && output.success && output.parsed_data ? (
            <div>
              <span className="font-medium text-gray-600">Parsed Formation:</span>
              <div className="mt-1 space-y-1 text-sm">
                <p><span className="text-gray-600">Title:</span> {output.parsed_data.title || 'N/A'}</p>
                <p><span className="text-gray-600">View:</span> {output.parsed_data.view || 'N/A'}</p>
                <p><span className="text-gray-600">Players:</span> {output.parsed_data.players?.length || 0}</p>
                {output.parser_used && (
                  <p><span className="text-gray-600">Parser:</span> {output.parser_used}</p>
                )}
                {output.parsed_data.players && output.parsed_data.players.length > 0 && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-gray-600 hover:text-gray-800">Show player details</summary>
                    <pre className="mt-1 text-xs bg-gray-50 p-2 rounded overflow-x-auto">
                      {JSON.stringify(output.parsed_data.players, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          ) : (
            <div>
              <span className="font-medium text-gray-600">Parse Result:</span>
              <p className="text-sm text-gray-800 mt-1">
                {output && typeof output === 'object' ? 
                  (output.success ? '✅ Success' : `❌ ${output.error || 'Failed'}`) : 
                  (output || 'N/A')}
              </p>
            </div>
          )}
        </div>
      )
    }
    
    if (trace.name === 'generate_diagram_from_spec') {
      return (
        <div className="space-y-2">
          <div>
            <span className="font-medium text-gray-600">Status:</span>
            <p className="text-sm text-gray-800 mt-1">
              {output && typeof output === 'object' && output.success ? '✅ Diagram generated successfully' : '❌ Generation failed'}
            </p>
          </div>
          {output && typeof output === 'object' && (output.diagram_path || output.filename) && (
            <div>
              <span className="font-medium text-gray-600">Output File:</span>
              <p className="text-sm text-gray-800 mt-1 font-mono text-xs break-all">
                {output.filename || output.diagram_path}
              </p>
            </div>
          )}
          {args && typeof args === 'object' && args.diagram_spec && (
            <details className="mt-2">
              <summary className="cursor-pointer text-gray-600 hover:text-gray-800 text-sm">Show diagram spec</summary>
              <pre className="mt-1 text-xs bg-gray-50 p-2 rounded overflow-x-auto">
                {typeof args.diagram_spec === 'string' ? 
                  JSON.stringify(JSON.parse(args.diagram_spec), null, 2) : 
                  JSON.stringify(args.diagram_spec, null, 2)}
              </pre>
            </details>
          )}
        </div>
      )
    }
    
    return (
      <div className="text-sm text-gray-600">
        <pre className="whitespace-pre-wrap overflow-x-auto">
          {JSON.stringify({ args, output }, null, 2)}
        </pre>
      </div>
    )
  }

  const message = extractMessage(parserSpec)

  return (
    <div className="space-y-6">
      {/* Current Diagram Specification */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Current Diagram Specification</h3>
        {parserSpec && typeof parserSpec === 'object' && (parserSpec.players || parserSpec.title || parserSpec.diagram_type) ? (
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="space-y-2 text-sm">
              {parserSpec.title && (
                <div>
                  <span className="font-medium text-blue-900">Title:</span> {parserSpec.title}
                </div>
              )}
              {parserSpec.diagram_type && (
                <div>
                  <span className="font-medium text-blue-900">Type:</span> {parserSpec.diagram_type}
                </div>
              )}
              {parserSpec.view && (
                <div>
                  <span className="font-medium text-blue-900">View:</span> {parserSpec.view}
                </div>
              )}
              {parserSpec.players && (
                <div>
                  <span className="font-medium text-blue-900">Players ({parserSpec.players.length}):</span>
                  <div className="mt-2 bg-white rounded p-2 overflow-x-auto">
                    <pre className="text-xs">{JSON.stringify(parserSpec.players, null, 2)}</pre>
                  </div>
                </div>
              )}
              {parserSpec.movements && parserSpec.movements.length > 0 && (
                <div>
                  <span className="font-medium text-blue-900">Movements ({parserSpec.movements.length}):</span>
                  <div className="mt-2 bg-white rounded p-2 overflow-x-auto">
                    <pre className="text-xs">{JSON.stringify(parserSpec.movements, null, 2)}</pre>
                  </div>
                </div>
              )}
              {parserSpec.annotations && parserSpec.annotations.length > 0 && (
                <div>
                  <span className="font-medium text-blue-900">Annotations:</span>
                  <div className="mt-2 bg-white rounded p-2 overflow-x-auto">
                    <pre className="text-xs">{JSON.stringify(parserSpec.annotations, null, 2)}</pre>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : message ? (
          <div className="bg-blue-50 rounded-lg p-4 space-y-2">
            <p className="text-sm font-medium text-blue-900">{message.status}</p>
            {message.description && (
              <p className="text-sm text-blue-700">{message.description}</p>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-500">No specification available</p>
        )}
      </div>

      {/* Agent Execution Steps */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Execution Steps</h3>
        {agentTraces && agentTraces.length > 0 ? (
          <div className="space-y-3">
            {agentTraces.map((trace, index) => {
              console.log(`Trace ${index}:`, trace)
              return (
                <div key={index} className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="flex items-center justify-center w-6 h-6 text-xs font-medium text-white bg-blue-600 rounded-full">
                        {trace.order || index + 1}
                      </span>
                      <span className="font-medium text-gray-900">
                        {trace.name === 'parse_hockey_formation' ? '🎯 Parse Formation' :
                         trace.name === 'generate_diagram_from_spec' ? '🎨 Generate Diagram' :
                         trace.name}
                      </span>
                    </div>
                  </div>
                  <div className="ml-8">
                    {renderToolDetails(trace)}
                  </div>
                </div>
              )
            })}
          </div>
        ) : parserSpec ? (
          // Fallback when no traces but we have a spec
          <div className="space-y-3">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <span className="flex items-center justify-center w-6 h-6 text-xs font-medium text-white bg-blue-600 rounded-full">
                  1
                </span>
                <span className="font-medium text-gray-900">🎯 Parse Formation</span>
              </div>
              <div className="ml-8">
                <div className="space-y-2">
                  <div>
                    <span className="font-medium text-gray-600">Input:</span>
                    <p className="text-sm text-gray-800 mt-1">{typeof parserSpec === 'string' ? 'Formation request' : 'N/A'}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Parse Result:</span>
                    <p className="text-sm text-gray-800 mt-1">N/A</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <span className="flex items-center justify-center w-6 h-6 text-xs font-medium text-white bg-blue-600 rounded-full">
                  2
                </span>
                <span className="font-medium text-gray-900">🎨 Generate Diagram</span>
              </div>
              <div className="ml-8">
                <div className="space-y-2">
                  <div>
                    <span className="font-medium text-gray-600">Status:</span>
                    <p className="text-sm text-gray-800 mt-1">
                      ❌ Generation failed
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <p className="text-sm text-gray-500">No execution steps recorded</p>
        )}
      </div>
    </div>
  )
}