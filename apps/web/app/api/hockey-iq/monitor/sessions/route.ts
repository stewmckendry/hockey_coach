/**
 * Hockey IQ Monitor - Sessions API
 * 
 * GET /api/hockey-iq/monitor/sessions - List all sessions
 */

import { NextRequest, NextResponse } from 'next/server'
import { SessionManager } from '@/lib/server/sessionManager'
import { monitorStorage } from '@/lib/server/monitorStorage'
import { SessionListResponse, MonitorFilters } from '@/lib/types/monitoring'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    
    // Parse query parameters for filtering
    const filters: MonitorFilters = {
      timeRange: searchParams.get('startDate') && searchParams.get('endDate') ? {
        start: searchParams.get('startDate')!,
        end: searchParams.get('endDate')!
      } : undefined,
      mode: searchParams.get('mode') as ('chat' | 'quiz' | 'mixed') || undefined,
      minInteractions: searchParams.get('minInteractions') ? parseInt(searchParams.get('minInteractions')!) : undefined,
      ipAddress: searchParams.get('ipAddress') || undefined
    }
    
    const limit = searchParams.get('limit') ? parseInt(searchParams.get('limit')!) : 50
    const sortBy = searchParams.get('sortBy') as 'timestamp' | 'processingTime' | 'score' | 'interactions' || 'timestamp'
    const sortOrder = searchParams.get('sortOrder') as 'asc' | 'desc' || 'desc'
    
    // Get sessions from both in-memory (current) and persistent storage
    let allSessions = SessionManager.getAllSessions()
    
    // Also load from persistent storage and merge
    const persistedSessions = monitorStorage.loadSessions()
    const persistedSessionsList = Object.values(persistedSessions)
    
    // Merge sessions, preferring in-memory versions for active sessions
    const sessionMap = new Map()
    
    // Add persisted sessions first
    persistedSessionsList.forEach(session => {
      sessionMap.set(session.sessionId, session)
    })
    
    // Add/update with in-memory sessions (these are more current)
    allSessions.forEach(session => {
      sessionMap.set(session.sessionId, session)
    })
    
    allSessions = Array.from(sessionMap.values())
    
    // Apply filters
    let filteredSessions = allSessions.filter(session => {
      // Time range filter
      if (filters.timeRange) {
        const sessionTime = new Date(session.startTime)
        const start = new Date(filters.timeRange.start)
        const end = new Date(filters.timeRange.end)
        if (sessionTime < start || sessionTime > end) return false
      }
      
      // Mode filter
      if (filters.mode && session.mode !== filters.mode) return false
      
      // Minimum interactions filter
      if (filters.minInteractions && session.totalInteractions < filters.minInteractions) return false
      
      // IP address filter (partial match)
      if (filters.ipAddress && !session.ipAddress.includes(filters.ipAddress)) return false
      
      return true
    })
    
    // Apply sorting
    filteredSessions.sort((a, b) => {
      let comparison = 0
      
      switch (sortBy) {
        case 'timestamp':
          comparison = new Date(a.lastActivity).getTime() - new Date(b.lastActivity).getTime()
          break
        case 'interactions':
          comparison = a.totalInteractions - b.totalInteractions
          break
        default:
          comparison = new Date(a.lastActivity).getTime() - new Date(b.lastActivity).getTime()
      }
      
      return sortOrder === 'desc' ? -comparison : comparison
    })
    
    // Apply limit
    const paginatedSessions = filteredSessions.slice(0, limit)
    
    // Calculate counts
    const activeCount = filteredSessions.filter(s => s.isActive).length
    
    const response: SessionListResponse = {
      success: true,
      sessions: paginatedSessions,
      totalCount: filteredSessions.length,
      activeCount: activeCount,
      timestamp: new Date().toISOString()
    }
    
    console.log(`[Monitor][API] Sessions endpoint: returning ${paginatedSessions.length}/${filteredSessions.length} sessions`)
    
    return NextResponse.json(response)
    
  } catch (error) {
    console.error('[Monitor][API] Sessions endpoint error:', error)
    
    return NextResponse.json({
      success: false,
      error: 'Failed to retrieve sessions',
      sessions: [],
      totalCount: 0,
      activeCount: 0,
      timestamp: new Date().toISOString()
    }, { status: 500 })
  }
}

// Export OPTIONS for CORS if needed
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}