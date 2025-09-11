/**
 * Hockey IQ Monitor - Chat History API
 * 
 * GET /api/hockey-iq/monitor/chat/[sessionId] - Get chat history for specific session
 */

import { NextRequest, NextResponse } from 'next/server'
import { SessionManager } from '@/lib/server/sessionManager'
import { monitorStorage } from '@/lib/server/monitorStorage'
import { ChatHistoryResponse } from '@/lib/types/monitoring'

interface RouteParams {
  sessionId: string
}

export async function GET(
  request: NextRequest, 
  { params }: { params: RouteParams }
) {
  try {
    const { sessionId } = params
    
    if (!sessionId) {
      return NextResponse.json({
        success: false,
        error: 'Session ID is required',
        sessionId: '',
        interactions: [],
        sessionInfo: null,
        totalCount: 0,
        timestamp: new Date().toISOString()
      }, { status: 400 })
    }
    
    // Get session info from both sources
    let sessionInfo = SessionManager.getSession(sessionId)
    
    if (!sessionInfo) {
      // Try persistent storage
      const persistedSessions = monitorStorage.loadSessions()
      sessionInfo = persistedSessions[sessionId]
    }
    
    if (!sessionInfo) {
      return NextResponse.json({
        success: false,
        error: 'Session not found',
        sessionId,
        interactions: [],
        sessionInfo: null,
        totalCount: 0,
        timestamp: new Date().toISOString()
      }, { status: 404 })
    }
    
    // Get chat interactions from both sources
    let interactions = SessionManager.getChatInteractions(sessionId)
    
    if (interactions.length === 0) {
      // Try persistent storage
      const persistedInteractions = monitorStorage.loadChatInteractions()
      interactions = persistedInteractions[sessionId] || []
    }
    
    // Sort interactions by timestamp (newest first for display)
    interactions.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    
    const response: ChatHistoryResponse = {
      success: true,
      sessionId,
      interactions,
      sessionInfo,
      totalCount: interactions.length,
      timestamp: new Date().toISOString()
    }
    
    console.log(`[Monitor][API] Chat history for ${sessionId}: ${interactions.length} interactions`)
    
    return NextResponse.json(response)
    
  } catch (error) {
    console.error(`[Monitor][API] Chat history error for ${params?.sessionId}:`, error)
    
    return NextResponse.json({
      success: false,
      error: 'Failed to retrieve chat history',
      sessionId: params?.sessionId || '',
      interactions: [],
      sessionInfo: null,
      totalCount: 0,
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