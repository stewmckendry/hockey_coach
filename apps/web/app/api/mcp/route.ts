import { NextRequest, NextResponse } from 'next/server'

const HOCKEY_MCP_DIRECT_URL = process.env.HOCKEY_MCP_DIRECT_URL || 'http://localhost:3003'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    if (!body.tool) {
      return NextResponse.json(
        { error: 'Missing required field: tool' },
        { status: 400 }
      )
    }

    // Call the direct hockey MCP API
    const response = await fetch(`${HOCKEY_MCP_DIRECT_URL}/api/mcp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        tool: body.tool,
        parameters: body.parameters || {}
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        { error: errorData.detail || `Hockey MCP API error: ${response.statusText}` },
        { status: response.status }
      )
    }

    const result = await response.json()
    
    return NextResponse.json(result)

  } catch (error) {
    console.error('API route error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function GET() {
  // Health check via direct hockey MCP API
  try {
    const response = await fetch(`${HOCKEY_MCP_DIRECT_URL}/api/mcp`, {
      method: 'GET',
    })

    const result = await response.json()
    return NextResponse.json(result, { 
      status: result.status === 'healthy' ? 200 : 503 
    })

  } catch (error) {
    return NextResponse.json({
      status: 'unhealthy',
      mcpServer: {
        url: HOCKEY_MCP_DIRECT_URL,
        protocol: 'FastMCP Direct',
        connected: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      timestamp: new Date().toISOString()
    }, { status: 503 })
  }
}

// OPTIONS handler for CORS
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
