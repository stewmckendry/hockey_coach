import { NextRequest, NextResponse } from 'next/server'

// TODO: Add authentication middleware
// TODO: Add rate limiting
// TODO: Add request/response logging

const MCP_BRIDGE_URL = process.env.MCP_BRIDGE_URL || 'http://localhost:3002'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Validate request body - expecting tool and parameters
    if (!body.tool) {
      return NextResponse.json(
        { error: 'Missing required field: tool' },
        { status: 400 }
      )
    }

    // Forward request to Python MCP bridge service
    const bridgeResponse = await fetch(`${MCP_BRIDGE_URL}/api/mcp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        tool: body.tool,
        parameters: body.parameters || body.arguments || {}
      }),
    })

    if (!bridgeResponse.ok) {
      console.error(`MCP bridge error: ${bridgeResponse.status}`)
      return NextResponse.json(
        { error: 'Failed to communicate with coaching AI bridge' },
        { status: bridgeResponse.status }
      )
    }

    const data = await bridgeResponse.json()
    
    return NextResponse.json(data)

  } catch (error) {
    console.error('API route error:', error)
    
    // Handle specific error types
    if (error instanceof SyntaxError) {
      return NextResponse.json(
        { error: 'Invalid JSON in request body' },
        { status: 400 }
      )
    }
    
    if (error instanceof TypeError && error.message.includes('fetch')) {
      return NextResponse.json(
        { error: 'Unable to connect to coaching AI bridge service' },
        { status: 503 }
      )
    }

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function GET() {
  // Health check endpoint
  try {
    // Forward health check to Python MCP bridge
    const healthResponse = await fetch(`${MCP_BRIDGE_URL}/api/mcp`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const isHealthy = healthResponse.ok
    const data = await healthResponse.json().catch(() => ({}))
    
    return NextResponse.json({
      status: isHealthy ? 'healthy' : 'unhealthy',
      mcpBridge: {
        url: MCP_BRIDGE_URL,
        status: healthResponse.status,
      },
      mcpServer: data.mcpServer || {},
      timestamp: new Date().toISOString()
    }, {
      status: isHealthy ? 200 : 503
    })

  } catch (error) {
    return NextResponse.json({
      status: 'unhealthy',
      mcpBridge: {
        url: MCP_BRIDGE_URL,
        error: 'Connection failed'
      },
      timestamp: new Date().toISOString()
    }, {
      status: 503
    })
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
