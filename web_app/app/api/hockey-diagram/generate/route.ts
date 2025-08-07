import { NextRequest, NextResponse } from 'next/server'
import { hockeyDiagramLogger } from '@/lib/server/hockeyDiagramLogger'
import { HockeyDiagramExpertHTTP, generateDiagramDirectMCP } from '@/lib/server/hockeyDiagramExpert'

// Configure route segment to allow longer execution time
export const maxDuration = 90 // 90 seconds timeout for agent processing

// Generate hockey diagram using the agent with fallback to direct MCP
async function generateHockeyDiagram(prompt: string, sessionId?: string) {
  try {
    // Try using the agent first
    const agent = new HockeyDiagramExpertHTTP(sessionId)
    
    try {
      await agent.initialize()
      const result = await agent.generate_diagram(prompt)
      
      // Transform agent result to our expected format
      let parserSpec = null
      if (result.explanation) {
        try {
          // Try to parse if it looks like JSON
          if (typeof result.explanation === 'string' && (result.explanation.trim().startsWith('{') || result.explanation.trim().startsWith('['))) {
            parserSpec = JSON.parse(result.explanation)
          } else {
            // Otherwise keep as is (it might be RunResult text or other format)
            parserSpec = result.explanation
          }
        } catch (e) {
          // If parsing fails, keep the original string
          parserSpec = result.explanation
        }
      }
      
      return {
        success: result.success,
        imageBase64: result.diagram_base64,
        processingTimeMs: result.metadata?.processing_time_ms || 0,
        toolsUsed: result.metadata?.tools_used || [],
        parserType: result.metadata?.parser_type || 'agent',
        parserSpec,
        agentTraces: result.metadata?.traces || [],
        error: result.error
      }
    } catch (agentError) {
      console.warn('Agent not available, falling back to direct MCP:', agentError)
      
      // Fallback to direct MCP call
      const result = await generateDiagramDirectMCP(prompt)
      
      // Handle parser spec safely for direct MCP too
      let parserSpecFallback = null
      if (result.explanation) {
        try {
          if (typeof result.explanation === 'string' && (result.explanation.trim().startsWith('{') || result.explanation.trim().startsWith('['))) {
            parserSpecFallback = JSON.parse(result.explanation)
          } else {
            parserSpecFallback = result.explanation
          }
        } catch (e) {
          parserSpecFallback = result.explanation
        }
      }
      
      return {
        success: result.success,
        imageBase64: result.diagram_base64,
        processingTimeMs: result.metadata?.processing_time_ms || 0,
        toolsUsed: result.metadata?.tools_used || [],
        parserType: result.metadata?.parser_type || 'direct_mcp',
        parserSpec: parserSpecFallback,
        agentTraces: result.metadata?.traces || [],
        error: result.error
      }
    }
  } catch (error) {
    console.error('Failed to generate diagram:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to generate diagram',
      processingTimeMs: 0,
      toolsUsed: []
    }
  }
}

export async function POST(request: NextRequest) {
  try {
    const { prompt } = await request.json()
    
    if (!prompt || typeof prompt !== 'string') {
      return NextResponse.json(
        { error: 'Prompt is required' },
        { status: 400 }
      )
    }

    // Get client metadata
    const sessionId = request.headers.get('x-session-id') || undefined
    const ipAddress = request.headers.get('x-forwarded-for') || 
                     request.headers.get('x-real-ip') || 
                     undefined

    // Generate the diagram with session ID for conversation context
    const result = await generateHockeyDiagram(prompt, sessionId)

    // Log the generation
    const logId = await hockeyDiagramLogger.logGeneration(
      prompt,
      result,
      { sessionId, ipAddress }
    )

    // Return result with log ID for feedback
    return NextResponse.json({
      ...result,
      logId
    })
  } catch (error) {
    console.error('Generate API error:', error)
    return NextResponse.json(
      { 
        success: false,
        error: 'Internal server error',
        processingTimeMs: 0,
        toolsUsed: []
      },
      { status: 500 }
    )
  }
}