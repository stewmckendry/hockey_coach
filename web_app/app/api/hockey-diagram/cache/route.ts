import { NextRequest, NextResponse } from 'next/server'

const MCP_BASE_URL = process.env.HOCKEY_DIAGRAM_MCP_URL || 'http://localhost:8001'

interface CacheOperation {
  action: 'save' | 'search' | 'get' | 'update' | 'delete' | 'stats'
  data?: any
}

// Helper function to call MCP tools
async function callMCPTool(toolName: string, args: any = {}) {
  try {
    const response = await fetch(`${MCP_BASE_URL}/mcp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: Date.now(),
        method: 'tools/call',
        params: {
          name: toolName,
          arguments: args
        }
      })
    })

    if (!response.ok) {
      throw new Error(`MCP request failed: ${response.statusText}`)
    }

    const result = await response.json()
    
    if (result.error) {
      throw new Error(result.error.message || 'MCP tool call failed')
    }

    // Parse the content if it's a JSON string
    if (result.result?.content?.[0]?.text) {
      try {
        return JSON.parse(result.result.content[0].text)
      } catch {
        return result.result.content[0].text
      }
    }

    return result.result
  } catch (error) {
    console.error(`Error calling MCP tool ${toolName}:`, error)
    throw error
  }
}

export async function POST(request: NextRequest) {
  try {
    const body: CacheOperation = await request.json()
    const { action, data } = body

    let result: any

    switch (action) {
      case 'save':
        result = await callMCPTool('save_diagram_to_cache', {
          prompt: data.prompt,
          spec: data.spec,
          parser_type: data.parserType || 'unknown',
          tags: data.tags,
          author: data.author
        })
        break

      case 'search':
        result = await callMCPTool('search_cached_diagrams', {
          query: data.query,
          limit: data.limit || 10,
          min_similarity: data.minSimilarity || 0.7
        })
        break

      case 'get':
        result = await callMCPTool('get_cached_diagram', {
          diagram_id: data.diagramId,
          regenerate: data.regenerate || false
        })
        break

      case 'update':
        result = await callMCPTool('update_cached_diagram', {
          diagram_id: data.diagramId,
          spec: data.spec,
          validated: data.validated,
          tags: data.tags
        })
        break

      case 'delete':
        result = await callMCPTool('delete_cached_diagram', {
          diagram_id: data.diagramId
        })
        break

      case 'stats':
        result = await callMCPTool('get_cache_statistics')
        break

      default:
        return NextResponse.json(
          { error: `Invalid action: ${action}` },
          { status: 400 }
        )
    }

    return NextResponse.json(result)

  } catch (error) {
    console.error('Cache API error:', error)
    return NextResponse.json(
      { 
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred' 
      },
      { status: 500 }
    )
  }
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const action = searchParams.get('action')

  try {
    if (action === 'stats') {
      const result = await callMCPTool('get_cache_statistics')
      return NextResponse.json(result)
    }

    if (action === 'list') {
      // List all diagrams with pagination
      const limit = parseInt(searchParams.get('limit') || '50')
      const offset = parseInt(searchParams.get('offset') || '0')
      const sortBy = searchParams.get('sortBy') || 'created_at'
      const ascending = searchParams.get('ascending') === 'true'

      const result = await callMCPTool('list_all_cached_diagrams', {
        limit,
        offset,
        sort_by: sortBy,
        ascending
      })
      return NextResponse.json(result)
    }

    if (action === 'search') {
      const query = searchParams.get('query') || ''
      const limit = parseInt(searchParams.get('limit') || '10')
      const minSimilarity = parseFloat(searchParams.get('minSimilarity') || '0.7')

      const result = await callMCPTool('search_cached_diagrams', {
        query,
        limit,
        min_similarity: minSimilarity
      })
      return NextResponse.json(result)
    }

    if (action === 'get') {
      const diagramId = searchParams.get('id')
      if (!diagramId) {
        return NextResponse.json(
          { error: 'Diagram ID required' },
          { status: 400 }
        )
      }

      const regenerate = searchParams.get('regenerate') === 'true'
      const result = await callMCPTool('get_cached_diagram', {
        diagram_id: diagramId,
        regenerate
      })
      return NextResponse.json(result)
    }

    return NextResponse.json(
      { error: 'Invalid or missing action parameter' },
      { status: 400 }
    )

  } catch (error) {
    console.error('Cache API GET error:', error)
    return NextResponse.json(
      { 
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred' 
      },
      { status: 500 }
    )
  }
}