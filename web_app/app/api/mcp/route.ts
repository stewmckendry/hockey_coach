import { NextRequest, NextResponse } from 'next/server'

// TODO: Add authentication middleware
// TODO: Add rate limiting
// TODO: Add request/response logging

const MCP_SERVER_URL = process.env.MCP_SERVER_URL || 'http://localhost:8000'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Validate request body
    if (!body.tool || !body.arguments) {
      return NextResponse.json(
        { error: 'Missing required fields: tool and arguments' },
        { status: 400 }
      )
    }

    // Proxy request to MCP server
    const mcpResponse = await fetch(`${MCP_SERVER_URL}/tools/${body.tool}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // TODO: Add authentication headers
      },
      body: JSON.stringify(body.arguments),
    })

    if (!mcpResponse.ok) {
      console.error(`MCP server error: ${mcpResponse.status}`)
      return NextResponse.json(
        { error: 'Failed to communicate with coaching AI' },
        { status: mcpResponse.status }
      )
    }

    const data = await mcpResponse.json()
    
    return NextResponse.json({
      success: true,
      data: data,
      timestamp: new Date().toISOString()
    })

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
        { error: 'Unable to connect to coaching AI server' },
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
    const healthResponse = await fetch(`${MCP_SERVER_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const isHealthy = healthResponse.ok
    
    return NextResponse.json({
      status: isHealthy ? 'healthy' : 'unhealthy',
      mcpServer: {
        url: MCP_SERVER_URL,
        status: healthResponse.status,
      },
      timestamp: new Date().toISOString()
    }, {
      status: isHealthy ? 200 : 503
    })

  } catch (error) {
    return NextResponse.json({
      status: 'unhealthy',
      mcpServer: {
        url: MCP_SERVER_URL,
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
