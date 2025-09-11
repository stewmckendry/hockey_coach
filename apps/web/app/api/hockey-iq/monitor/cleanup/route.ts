/**
 * Hockey IQ Monitor - Cleanup API
 * 
 * POST /api/hockey-iq/monitor/cleanup - Clean up old monitoring data
 */

import { NextRequest, NextResponse } from 'next/server'
import { SessionManager } from '@/lib/server/sessionManager'
import { monitorStorage } from '@/lib/server/monitorStorage'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { retentionDays = 7, maxAgeHours = 24 } = body
    
    // Cleanup in-memory sessions
    const cleanedInMemory = SessionManager.cleanupInactiveSessions(maxAgeHours)
    
    // Cleanup persistent storage
    const cleanedPersistent = monitorStorage.cleanup(retentionDays)
    
    const result = {
      success: true,
      cleaned: {
        inMemorySessions: cleanedInMemory,
        persistentSessions: cleanedPersistent,
        total: cleanedInMemory + cleanedPersistent
      },
      retentionPolicy: {
        retentionDays,
        maxAgeHours
      },
      timestamp: new Date().toISOString()
    }
    
    console.log(`[Monitor][API] Cleanup completed: ${result.cleaned.total} sessions removed (${cleanedInMemory} in-memory, ${cleanedPersistent} persistent)`)
    
    return NextResponse.json(result)
    
  } catch (error) {
    console.error('[Monitor][API] Cleanup error:', error)
    
    return NextResponse.json({
      success: false,
      error: 'Failed to cleanup monitoring data',
      details: error instanceof Error ? error.message : 'Unknown error',
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
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}