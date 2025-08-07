import { NextRequest, NextResponse } from 'next/server'
import { hockeyDiagramLogger } from '@/lib/server/hockeyDiagramLogger'

// Simple auth check - in production, use proper authentication
const isAuthorized = (request: NextRequest): boolean => {
  const adminKey = request.headers.get('x-admin-key')
  return adminKey === process.env.HOCKEY_DIAGRAM_ADMIN_KEY || 
         process.env.NODE_ENV === 'development'
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
  const limit = parseInt(searchParams.get('limit') || '20')
  const includeFeedback = searchParams.get('includeFeedback') !== 'false'

  try {
    switch (action) {
      case 'recent': {
        const logs = hockeyDiagramLogger.getRecentLogs(limit, includeFeedback)
        return NextResponse.json({
          success: true,
          logs,
          count: logs.length
        })
      }

      case 'date': {
        if (!date) {
          return NextResponse.json(
            { error: 'Date parameter required' },
            { status: 400 }
          )
        }
        const logs = await hockeyDiagramLogger.getLogsForDate(date)
        return NextResponse.json({
          success: true,
          logs,
          count: logs.length,
          date
        })
      }

      case 'search': {
        if (!query) {
          return NextResponse.json(
            { error: 'Query parameter required' },
            { status: 400 }
          )
        }
        const logs = await hockeyDiagramLogger.searchLogs(query, date)
        return NextResponse.json({
          success: true,
          logs,
          count: logs.length,
          query,
          date
        })
      }

      case 'stats': {
        const stats = await hockeyDiagramLogger.getStatistics(date)
        return NextResponse.json({
          success: true,
          stats,
          date: date || 'today'
        })
      }

      case 'dates': {
        const dates = await hockeyDiagramLogger.getAvailableDates()
        return NextResponse.json({
          success: true,
          dates
        })
      }

      case 'detail': {
        const id = searchParams.get('id')
        if (!id) {
          return NextResponse.json(
            { error: 'ID parameter required' },
            { status: 400 }
          )
        }
        const log = await hockeyDiagramLogger.getLogById(id)
        if (!log) {
          return NextResponse.json(
            { error: 'Log not found' },
            { status: 404 }
          )
        }
        return NextResponse.json({
          success: true,
          log
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