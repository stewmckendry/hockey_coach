/**
 * Hockey IQ Monitor - Quiz History API
 * 
 * GET /api/hockey-iq/monitor/quiz/[sessionId] - Get quiz history for specific session
 */

import { NextRequest, NextResponse } from 'next/server'
import { SessionManager } from '@/lib/server/sessionManager'
import { monitorStorage } from '@/lib/server/monitorStorage'
import { QuizHistoryResponse } from '@/lib/types/monitoring'

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
        session: null,
        turns: [],
        sessionInfo: null,
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
        session: null,
        turns: [],
        sessionInfo: null,
        timestamp: new Date().toISOString()
      }, { status: 404 })
    }
    
    // Get quiz session from both sources
    let quizSession = SessionManager.getQuizSession(sessionId)
    
    if (!quizSession) {
      // Try persistent storage
      const persistedQuizSessions = monitorStorage.loadQuizSessions()
      quizSession = persistedQuizSessions[sessionId]
    }
    
    // Get quiz turns from both sources
    let turns = SessionManager.getQuizTurns(sessionId)
    
    if (turns.length === 0) {
      // Try persistent storage
      const persistedTurns = monitorStorage.loadQuizTurns()
      turns = persistedTurns[sessionId] || []
    }
    
    // Sort turns by timestamp (newest first for display)
    turns.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    
    const response: QuizHistoryResponse = {
      success: true,
      sessionId,
      session: quizSession || {
        sessionId,
        startTime: sessionInfo.startTime,
        lastActivity: sessionInfo.lastActivity,
        questionBank: [],
        questionsAsked: [],
        questionsRemaining: [],
        currentQuestionIndex: 0,
        userScore: {
          correct: turns.filter(t => t.isCorrect).length,
          total: turns.length,
          streak: 0,
          longestStreak: 0
        },
        categoryStats: {},
        regenerationThreshold: 10,
        difficulty: 'rookie',
        preferences: {
          includeThunderContext: true,
          preferredCategories: []
        }
      },
      turns,
      sessionInfo,
      timestamp: new Date().toISOString()
    }
    
    console.log(`[Monitor][API] Quiz history for ${sessionId}: ${turns.length} turns, ${quizSession ? 'session found' : 'session reconstructed'}`)
    
    return NextResponse.json(response)
    
  } catch (error) {
    console.error(`[Monitor][API] Quiz history error for ${params?.sessionId}:`, error)
    
    return NextResponse.json({
      success: false,
      error: 'Failed to retrieve quiz history',
      sessionId: params?.sessionId || '',
      session: null,
      turns: [],
      sessionInfo: null,
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