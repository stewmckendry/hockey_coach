import { NextRequest, NextResponse } from 'next/server'
import { hockeyIQLogger } from '@/lib/server/hockeyIQLogger'

// Simple auth check - in production, use proper authentication
const isAuthorized = (request: NextRequest): boolean => {
  // For MVP, check for a simple admin key in headers
  const adminKey = request.headers.get('x-admin-key')
  return adminKey === process.env.HOCKEY_IQ_ADMIN_KEY || 
         process.env.NODE_ENV === 'development' // Allow in dev mode
}

export async function GET(request: NextRequest) {
  // Check authorization
  if (!isAuthorized(request)) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }

  const { searchParams } = new URL(request.url)
  const action = searchParams.get('action') || 'recent'
  const date = searchParams.get('date')
  const query = searchParams.get('query')
  const limit = parseInt(searchParams.get('limit') || '50')

  try {
    switch (action) {
      case 'recent': {
        // Get recent logs from memory
        const logs = hockeyIQLogger.getRecentLogs(limit)
        return NextResponse.json({
          success: true,
          logs,
          count: logs.length
        })
      }

      case 'date': {
        // Get logs for specific date
        if (!date) {
          return NextResponse.json(
            { error: 'Date parameter required' },
            { status: 400 }
          )
        }
        const logs = await hockeyIQLogger.getLogsForDate(date)
        return NextResponse.json({
          success: true,
          logs,
          count: logs.length,
          date
        })
      }

      case 'search': {
        // Search logs
        if (!query) {
          return NextResponse.json(
            { error: 'Query parameter required' },
            { status: 400 }
          )
        }
        const logs = await hockeyIQLogger.searchLogs(query, date ?? undefined)
        return NextResponse.json({
          success: true,
          logs,
          count: logs.length,
          query,
          date
        })
      }

      case 'stats': {
        // Get statistics
        const stats = await hockeyIQLogger.getStatistics(date ?? undefined)
        return NextResponse.json({
          success: true,
          stats,
          date: date || 'today'
        })
      }

      case 'dates': {
        // Get available log dates
        const dates = await hockeyIQLogger.getAvailableDates()
        return NextResponse.json({
          success: true,
          dates
        })
      }

      default:
        return NextResponse.json(
          { error: 'Invalid action' },
          { status: 400 }
        )
    }
  } catch (error) {
    console.error('Monitor API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// SSE endpoint for real-time monitoring
export async function POST(request: NextRequest) {
  if (!isAuthorized(request)) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }

  // For real-time updates, we'd implement SSE here
  // For MVP, just return current stats
  const stats = await hockeyIQLogger.getStatistics()
  const recentLogs = hockeyIQLogger.getRecentLogs(10)
  
  return NextResponse.json({
    success: true,
    stats,
    recentLogs,
    timestamp: new Date().toISOString()
  })
}