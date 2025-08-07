/**
 * Hockey Diagram Expert Agent
 * Wrapper for the Python hockey diagram agent
 */

import { spawn } from 'child_process'
import path from 'path'

export interface DiagramResult {
  success: boolean
  diagram_base64?: string
  explanation?: string
  metadata?: {
    tools_used: string[]
    parser_type?: string
    processing_time_ms: number
    traces?: any[]
  }
  error?: string
}

export class HockeyDiagramExpert {
  private pythonPath: string
  private scriptPath: string
  private conversationId?: string

  constructor(conversationId?: string) {
    // Adjust paths based on your environment
    this.pythonPath = path.join(process.cwd(), '..', '..', 'spacy_env', 'bin', 'python')
    this.scriptPath = path.join(process.cwd(), '..', 'servers', 'hockey_diagram_mcp', 'hockey_diagram_agent.py')
    this.conversationId = conversationId
  }

  async initialize(): Promise<void> {
    // In the TypeScript version, we don't need to initialize the agent
    // as we'll spawn a new Python process for each request
  }

  async generate_diagram(request: string): Promise<DiagramResult> {
    return new Promise((resolve, reject) => {
      const args = ['generate', request]
      if (this.conversationId) {
        args.push('--conversation-id', this.conversationId)
      }

      const pythonProcess = spawn(this.pythonPath, [this.scriptPath, ...args], {
        env: {
          ...process.env,
          PYTHONPATH: path.join(process.cwd(), '..')
        }
      })

      let output = ''
      let errorOutput = ''

      pythonProcess.stdout.on('data', (data) => {
        output += data.toString()
      })

      pythonProcess.stderr.on('data', (data) => {
        errorOutput += data.toString()
      })

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          console.error('Python process error:', errorOutput)
          resolve({
            success: false,
            error: errorOutput || 'Failed to generate diagram',
            metadata: {
              tools_used: [],
              processing_time_ms: 0
            }
          })
          return
        }

        try {
          // Parse the JSON output from the Python script
          const result = JSON.parse(output)
          resolve(result)
        } catch (error) {
          console.error('Failed to parse agent output:', error)
          resolve({
            success: false,
            error: 'Failed to parse agent output',
            metadata: {
              tools_used: [],
              processing_time_ms: 0
            }
          })
        }
      })

      pythonProcess.on('error', (error) => {
        console.error('Failed to spawn Python process:', error)
        reject(error)
      })
    })
  }
}

/**
 * Alternative implementation using direct HTTP call to the agent server
 * This is cleaner and more scalable than spawning Python processes
 */
export class HockeyDiagramExpertHTTP {
  private agentUrl: string
  private conversationId?: string

  constructor(conversationId?: string) {
    // Assuming the hockey diagram agent is running as an HTTP server
    this.agentUrl = process.env.HOCKEY_DIAGRAM_AGENT_URL || 'http://localhost:8001'
    this.conversationId = conversationId
  }

  async initialize(): Promise<void> {
    // Check if agent is available
    try {
      const response = await fetch(`${this.agentUrl}/health`)
      if (!response.ok) {
        throw new Error('Hockey diagram agent is not available')
      }
    } catch (error) {
      console.error('Failed to connect to hockey diagram agent:', error)
      throw error
    }
  }

  async generate_diagram(request: string): Promise<DiagramResult> {
    try {
      const startTime = Date.now()
      
      // Create an AbortController with 90 second timeout (agent can take up to 60s)
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 90000)
      
      console.log(`Sending request to agent at ${this.agentUrl}/generate`)
      
      const response = await fetch(`${this.agentUrl}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          request,
          conversation_id: this.conversationId
        }),
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)

      if (!response.ok) {
        throw new Error(`Agent server error: ${response.status}`)
      }

      const result = await response.json()
      
      // Ensure metadata includes processing time
      if (result.metadata) {
        result.metadata.processing_time_ms = Date.now() - startTime
      } else {
        result.metadata = {
          tools_used: [],
          processing_time_ms: Date.now() - startTime
        }
      }

      return result
    } catch (error) {
      console.error('Failed to generate diagram:', error)
      
      // Provide more specific error messages
      let errorMessage = 'Failed to generate diagram'
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorMessage = 'Request timed out after 90 seconds'
        } else if (error.message.includes('fetch')) {
          errorMessage = 'Failed to connect to agent server at ' + this.agentUrl
        } else {
          errorMessage = error.message
        }
      }
      
      return {
        success: false,
        error: errorMessage,
        metadata: {
          tools_used: [],
          processing_time_ms: Date.now() - (error instanceof Error && 'startTime' in error ? (error as any).startTime : Date.now())
        }
      }
    }
  }
}

/**
 * Fallback to direct MCP call if agent is not available
 */
export async function generateDiagramDirectMCP(prompt: string): Promise<DiagramResult> {
  try {
    const startTime = Date.now()
    
    const response = await fetch('http://localhost:8001/mcp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'tools/call',
        params: {
          name: 'create_hockey_diagram',
          arguments: {
            request: prompt
          }
        },
        id: 1
      })
    })

    if (!response.ok) {
      throw new Error(`MCP server error: ${response.status}`)
    }

    const result = await response.json()
    
    console.log('MCP Response:', JSON.stringify(result, null, 2))
    
    if (result.error) {
      throw new Error(result.error.message || 'MCP error')
    }

    const processingTime = Date.now() - startTime
    
    // Parse the MCP result - handle both direct result and nested content structure
    let diagramResult = result.result
    
    // MCP tools often return content array with text items
    if (diagramResult?.content && Array.isArray(diagramResult.content)) {
      // Extract the text content and parse it
      const textContent = diagramResult.content.find((item: any) => item.type === 'text')
      if (textContent?.text) {
        try {
          diagramResult = JSON.parse(textContent.text)
        } catch (e) {
          console.error('Failed to parse MCP content:', e)
          diagramResult = { error: 'Failed to parse MCP response' }
        }
      }
    }
    
    // Check if we got a valid result - log the structure for debugging
    console.log('Parsed diagram result:', JSON.stringify(diagramResult, null, 2))
    
    if (!diagramResult || (!diagramResult.diagram_base64 && !diagramResult.diagram_path)) {
      console.error('Invalid MCP result structure:', diagramResult)
      console.error('Full MCP response was:', JSON.stringify(result, null, 2))
      return {
        success: false,
        error: 'No diagram path in result',
        metadata: {
          tools_used: ['create_hockey_diagram'],
          processing_time_ms: processingTime
        }
      }
    }
    
    // Handle both diagram_path (file) and diagram_base64 (direct base64) formats
    let base64Image = diagramResult.diagram_base64
    
    if (!base64Image && diagramResult.diagram_path) {
      // If we got a file path instead of base64, read the file
      try {
        const fs = await import('fs/promises')
        
        // Read the file from the path
        const imageBuffer = await fs.readFile(diagramResult.diagram_path)
        base64Image = `data:image/png;base64,${imageBuffer.toString('base64')}`
        console.log('Successfully read diagram from file path:', diagramResult.diagram_path)
      } catch (fileError) {
        console.error('Failed to read diagram file:', fileError)
        return {
          success: false,
          error: `Failed to read diagram file: ${fileError}`,
          metadata: {
            tools_used: ['create_hockey_diagram'],
            processing_time_ms: processingTime
          }
        }
      }
    }
    
    return {
      success: diagramResult.success !== false,
      diagram_base64: base64Image,
      explanation: diagramResult.explanation || diagramResult.diagram_spec || diagramResult.spec || diagramResult.response,
      metadata: {
        tools_used: diagramResult.tools_used || ['create_hockey_diagram'],
        parser_type: diagramResult.parser_type || 'agent',
        processing_time_ms: processingTime,
        traces: diagramResult.traces || diagramResult.tool_calls_detail || []
      }
    }
  } catch (error) {
    console.error('Failed to generate diagram via MCP:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to generate diagram',
      metadata: {
        tools_used: [],
        processing_time_ms: 0
      }
    }
  }
}