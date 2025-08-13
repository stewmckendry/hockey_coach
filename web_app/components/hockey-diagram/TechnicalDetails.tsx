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
  arguments: string | any
  order: number
  output: string | any
  from_parser?: boolean
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
    const messageMatch = specStr.match(/✅\s*(.*?)\s*📁/)
    const formationMatch = specStr.match(/🏒\s*Formation:\s*(.*?)(?:\n|```|$)/)
    
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

  // Map tool names to user-friendly descriptions
  const toolDescriptions: Record<string, string> = {
    'parse_hockey_formation': '🎯 Parse Formation',
    'generate_diagram_from_spec': '🎨 Generate Diagram',
    'search_hockey_tactics': '🔍 Search Tactics Database',
    'search_hockey_drills': '📚 Search Drills Database',
    'search_hockey_videos': '🎥 Search Video Database',
    'search_hockey_skills': '⚡ Search Skills Database',
    'search_hockey_dryland': '🏃 Search Dryland Training',
    'search_hockey_dryland_videos': '📹 Search Training Videos',
    'search_hockey_nhl_insights': '🏆 Search NHL Insights',
    'search_hockey_rules': '📖 Search Hockey Rules',
    'web_search_exa': '🌐 Web Search',
    'synthesize_research_to_formation': '🔄 Synthesize Research',
    'map_formation_to_zones': '📍 Map to Zones',
    'list_hockey_formations': '📋 List Formations',
    'process_diagram_feedback': '✏️ Process Feedback'
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
                  (output.success ? '✅ Success' : 
                   output.error ? `❌ ${output.error}` : 
                   '✅ Completed') : 
                  (output ? '✅ Completed' : '⏳ Processing...')}
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
              {output && typeof output === 'object' && (output.success || output.diagram_path) ? 
                '✅ Diagram generated successfully' : 
                output && typeof output === 'object' && output.error ? 
                `❌ ${output.error}` :
                output ? '✅ Diagram generated' : '⏳ Generating diagram...'}
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
    
    // Handle research tools (search_hockey_tactics, search_hockey_drills, etc.)
    if (trace.name.includes('search_hockey_')) {
      return (
        <div className="space-y-2">
          <div>
            <span className="font-medium text-gray-600">Query:</span>
            <p className="text-sm text-gray-800 mt-1">
              {typeof args === 'object' && args.query ? args.query : 
               typeof args === 'object' && args.prompt ? args.prompt : 'N/A'}
            </p>
          </div>
          <div>
            <span className="font-medium text-gray-600">Results:</span>
            <p className="text-sm text-gray-800 mt-1">
              {output && typeof output === 'object' ? 
                (output.results ? `✅ Found ${output.results.length || 0} results` : 
                 output.n_results ? `✅ Found ${output.n_results} results` :
                 output.success === false ? '❌ Search failed' :
                 '✅ Results retrieved') : 
                '⏳ Searching...'}
            </p>
            {output && typeof output === 'object' && output.results && output.results.length > 0 && (
              <details className="mt-2">
                <summary className="cursor-pointer text-gray-600 hover:text-gray-800 text-sm">Show results preview</summary>
                <div className="mt-1 text-xs bg-gray-50 p-2 rounded overflow-x-auto max-h-48 overflow-y-auto">
                  {output.results.slice(0, 3).map((result: any, idx: number) => (
                    <div key={idx} className="mb-2 pb-2 border-b last:border-0">
                      <p className="font-medium">{result.title || result.name || `Result ${idx + 1}`}</p>
                      {result.content && <p className="text-gray-600 mt-1">{result.content.substring(0, 150)}...</p>}
                      {result.metadata && <p className="text-gray-500 mt-1">Score: {result.metadata.score?.toFixed(2) || 'N/A'}</p>}
                    </div>
                  ))}
                  {output.results.length > 3 && (
                    <p className="text-gray-500 mt-2">...and {output.results.length - 3} more results</p>
                  )}
                </div>
              </details>
            )}
          </div>
        </div>
      )
    }
    
    // Handle web search
    if (trace.name === 'web_search_exa') {
      return (
        <div className="space-y-2">
          <div>
            <span className="font-medium text-gray-600">Search Query:</span>
            <p className="text-sm text-gray-800 mt-1">
              {typeof args === 'object' && args.query ? args.query : 'N/A'}
            </p>
          </div>
          <div>
            <span className="font-medium text-gray-600">Results:</span>
            <p className="text-sm text-gray-800 mt-1">
              {output && typeof output === 'object' && output.results ? 
                `✅ Found ${output.results.length || 0} web results` : 
                '⏳ Searching web...'}
            </p>
          </div>
        </div>
      )
    }
    
    // Handle synthesis and mapping subagents
    if (trace.name === 'synthesize_research_to_formation' || trace.name === 'map_formation_to_zones') {
      return (
        <div className="space-y-2">
          <div>
            <span className="font-medium text-gray-600">Processing:</span>
            <p className="text-sm text-gray-800 mt-1">
              {trace.name === 'synthesize_research_to_formation' ? 
                'Converting research findings into structured formation data...' :
                'Mapping formation to precise zone coordinates...'}
            </p>
          </div>
          {output && (
            <div>
              <span className="font-medium text-gray-600">Status:</span>
              <p className="text-sm text-gray-800 mt-1">✅ Completed</p>
            </div>
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
                <div key={index} className={`${trace.from_parser ? 'ml-4 border-l-2 border-blue-300' : ''} bg-gray-50 rounded-lg p-4`}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className={`flex items-center justify-center w-6 h-6 text-xs font-medium text-white rounded-full ${
                        trace.from_parser ? 'bg-purple-600' : 'bg-blue-600'
                      }`}>
                        {trace.order || index + 1}
                      </span>
                      <span className="font-medium text-gray-900">
                        {toolDescriptions[trace.name] || trace.name}
                      </span>
                      {trace.from_parser && (
                        <span className="text-xs text-purple-600 font-medium">(Parser Agent)</span>
                      )}
                    </div>
                  </div>
                  <div className="ml-8">
                    {renderToolDetails(trace)}
                  </div>
                </div>
              )
            })}
          </div>
        ) : parserSpec && typeof parserSpec === 'object' && parserSpec.players ? (
          // Fallback when no traces but we have a valid spec - diagram was likely generated successfully
          <div className="space-y-3">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <span className="flex items-center justify-center w-6 h-6 text-xs font-medium text-white bg-green-600 rounded-full">
                  ✓
                </span>
                <span className="font-medium text-gray-900">🎨 Diagram Generated</span>
              </div>
              <div className="ml-8">
                <div className="space-y-2">
                  <div>
                    <span className="font-medium text-gray-600">Status:</span>
                    <p className="text-sm text-gray-800 mt-1">
                      ✅ Successfully generated from specification
                    </p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Details:</span>
                    <p className="text-sm text-gray-800 mt-1">
                      {parserSpec.players?.length || 0} players positioned • 
                      {parserSpec.movements?.length || 0} movements • 
                      {parserSpec.view || 'full'} view
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