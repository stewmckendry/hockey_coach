import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Test the raw MCP response to see its structure
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
            request: 'Power play 1-3-1 umbrella formation'
          }
        },
        id: 1
      })
    })

    const result = await response.json()
    
    // Return the raw structure for inspection
    return NextResponse.json({
      raw_response: result,
      has_result: !!result.result,
      has_content: !!result.result?.content,
      content_type: result.result?.content?.[0]?.type,
      parsed_attempt: (() => {
        try {
          if (result.result?.content?.[0]?.text) {
            return JSON.parse(result.result.content[0].text)
          }
        } catch (e) {
          return null
        }
      })()
    })
  } catch (error) {
    return NextResponse.json({
      error: error instanceof Error ? error.message : 'Unknown error',
      type: 'exception'
    }, { status: 500 })
  }
}