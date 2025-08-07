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
    
    const specStr = typeof spec === 'string' ? spec : JSON.stringify(spec)
    
    // Extract the message between ✅ and 🏒
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
      const args = JSON.parse(trace.arguments)
      const output = JSON.parse(trace.output)
      return { args, output }
    } catch {
      return { args: trace.arguments, output: trace.output }
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
            <p className="text-sm text-gray-800 mt-1">{args.prompt || args || 'N/A'}</p>
          </div>
          {output && output.success && output.parsed_data ? (
            <div>
              <span className="font-medium text-gray-600">Parsed Formation:</span>
              <div className="mt-1 space-y-1 text-sm">
                <p><span className="text-gray-600">Title:</span> {output.parsed_data.title || 'N/A'}</p>
                <p><span className="text-gray-600">View:</span> {output.parsed_data.view || 'N/A'}</p>
                <p><span className="text-gray-600">Players:</span> {output.parsed_data.players?.length || 0}</p>
              </div>
            </div>
          ) : (
            <div>
              <span className="font-medium text-gray-600">Parse Result:</span>
              <p className="text-sm text-gray-800 mt-1">{output && output.success ? 'Success' : 'N/A'}</p>
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
              {output.success ? '✅ Diagram generated successfully' : '❌ Generation failed'}
            </p>
          </div>
          {output.diagram_path && (
            <div>
              <span className="font-medium text-gray-600">Output File:</span>
              <p className="text-sm text-gray-800 mt-1 font-mono">{output.filename || output.diagram_path}</p>
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
      {/* Parser Specification */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Formation Details</h3>
        {message ? (
          <div className="bg-blue-50 rounded-lg p-4 space-y-2">
            <p className="text-sm font-medium text-blue-900">{message.status}</p>
            {message.description && (
              <p className="text-sm text-blue-700">{message.description}</p>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-500">No formation details available</p>
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
        ) : (
          <p className="text-sm text-gray-500">No execution steps recorded</p>
        )}
      </div>
    </div>
  )
}