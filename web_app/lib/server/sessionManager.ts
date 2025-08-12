/**
 * Hockey IQ Session Manager
 * 
 * Handles session creation, tracking, and management for the Hockey IQ Chatbot.
 * Provides utilities for capturing user context and managing session lifecycle.
 */

import { NextRequest } from 'next/server'
import { SessionLog, ChatInteraction, QuizSession, QuizTurn, PerformanceMetrics } from '@/lib/types/monitoring'
import crypto from 'crypto'

export class SessionManager {
  private static sessions: Map<string, SessionLog> = new Map()
  private static chatInteractions: Map<string, ChatInteraction[]> = new Map()
  private static quizSessions: Map<string, QuizSession> = new Map()
  private static quizTurns: Map<string, QuizTurn[]> = new Map()
  
  /**
   * Extract session information from request
   */
  static extractSessionInfo(request: NextRequest): {
    sessionId: string
    ipAddress: string
    userAgent: string
    timestamp: string
  } {
    // Get IP address (handle various proxy headers)
    const forwarded = request.headers.get('x-forwarded-for')
    const realIp = request.headers.get('x-real-ip')
    const ipAddress = forwarded?.split(',')[0].trim() || 
                     realIp || 
                     request.ip || 
                     '127.0.0.1'
    
    const userAgent = request.headers.get('user-agent') || 'Unknown'
    const timestamp = new Date().toISOString()
    
    // Get session ID from cookie or create new one
    let sessionCookie = request.cookies.get('hockey-iq-session')?.value
    
    // Check if the session cookie is invalid (e.g., just an IP address)
    if (sessionCookie && !sessionCookie.startsWith('hiq_')) {
      console.log(`[SessionManager] Invalid session cookie detected: ${sessionCookie}, generating new one`)
      sessionCookie = undefined  // Force generation of new ID
    }
    
    const sessionId = sessionCookie || this.generateSessionId(ipAddress, userAgent)
    
    return {
      sessionId,
      ipAddress,
      userAgent,
      timestamp
    }
  }
  
  /**
   * Generate unique session ID
   */
  private static generateSessionId(ipAddress: string, userAgent: string): string {
    const timestamp = Date.now()
    const random = crypto.randomBytes(8).toString('hex')
    const hash = crypto.createHash('sha256')
                      .update(`${ipAddress}-${userAgent}-${timestamp}-${random}`)
                      .digest('hex')
                      .substring(0, 12)
    
    return `hiq_${hash}`
  }
  
  /**
   * Create or update session
   */
  static createOrUpdateSession(
    sessionId: string, 
    ipAddress: string, 
    userAgent: string,
    mode: 'chat' | 'quiz' | 'mixed'
  ): SessionLog {
    const timestamp = new Date().toISOString()
    
    const existingSession = this.sessions.get(sessionId)
    
    if (existingSession) {
      // Update existing session
      existingSession.lastActivity = timestamp
      existingSession.totalInteractions += 1
      existingSession.isActive = true
      
      // Update mode if it changed to mixed
      if (existingSession.mode !== mode && existingSession.mode !== 'mixed') {
        existingSession.mode = existingSession.mode === mode ? mode : 'mixed'
      }
      
      this.sessions.set(sessionId, existingSession)
      return existingSession
    } else {
      // Create new session
      const newSession: SessionLog = {
        sessionId,
        ipAddress,
        userAgent,
        startTime: timestamp,
        lastActivity: timestamp,
        mode,
        totalInteractions: 1,
        isActive: true
      }
      
      this.sessions.set(sessionId, newSession)
      
      // Initialize interaction arrays
      this.chatInteractions.set(sessionId, [])
      this.quizTurns.set(sessionId, [])
      
      return newSession
    }
  }
  
  /**
   * Log chat interaction
   */
  static logChatInteraction(interaction: ChatInteraction): void {
    const interactions = this.chatInteractions.get(interaction.sessionId) || []
    interactions.push(interaction)
    this.chatInteractions.set(interaction.sessionId, interactions)
    
    // Update session
    this.createOrUpdateSession(
      interaction.sessionId,
      '', // IP will be updated by caller
      '', // User agent will be updated by caller  
      'chat'
    )
    
    console.log(`[Monitor][Chat][${interaction.sessionId}] ${interaction.question.substring(0, 50)}... (${interaction.processingTime}ms)`)
  }
  
  /**
   * Create or update quiz session
   */
  static createOrUpdateQuizSession(sessionId: string, session: Partial<QuizSession>): QuizSession {
    const existing = this.quizSessions.get(sessionId)
    const timestamp = new Date().toISOString()
    
    if (existing) {
      const updated = {
        ...existing,
        ...session,
        lastActivity: timestamp
      }
      this.quizSessions.set(sessionId, updated)
      return updated
    } else {
      const newSession: QuizSession = {
        sessionId,
        startTime: timestamp,
        lastActivity: timestamp,
        questionBank: [],
        questionsAsked: [],
        questionsRemaining: [],
        currentQuestionIndex: 0,
        userScore: {
          correct: 0,
          total: 0,
          streak: 0,
          longestStreak: 0
        },
        categoryStats: {},
        regenerationThreshold: 10,
        difficulty: 'rookie',
        preferences: {
          includeThunderContext: true,
          preferredCategories: []
        },
        ...session
      }
      
      this.quizSessions.set(sessionId, newSession)
      return newSession
    }
  }
  
  /**
   * Log quiz turn
   */
  static logQuizTurn(turn: QuizTurn): void {
    const turns = this.quizTurns.get(turn.sessionId) || []
    turns.push(turn)
    this.quizTurns.set(turn.sessionId, turns)
    
    // Update session
    this.createOrUpdateSession(
      turn.sessionId,
      '', // IP will be updated by caller
      '', // User agent will be updated by caller
      'quiz'
    )
    
    console.log(`[Monitor][Quiz][${turn.sessionId}] ${turn.category} question - ${turn.isCorrect ? 'Correct' : 'Incorrect'} (${turn.processingTime}ms)`)
  }
  
  /**
   * Get session information
   */
  static getSession(sessionId: string): SessionLog | undefined {
    return this.sessions.get(sessionId)
  }
  
  /**
   * Get all sessions
   */
  static getAllSessions(): SessionLog[] {
    return Array.from(this.sessions.values())
      .sort((a, b) => new Date(b.lastActivity).getTime() - new Date(a.lastActivity).getTime())
  }
  
  /**
   * Get chat interactions for session
   */
  static getChatInteractions(sessionId: string): ChatInteraction[] {
    return this.chatInteractions.get(sessionId) || []
  }
  
  /**
   * Get quiz session
   */
  static getQuizSession(sessionId: string): QuizSession | undefined {
    return this.quizSessions.get(sessionId)
  }
  
  /**
   * Get quiz turns for session
   */
  static getQuizTurns(sessionId: string): QuizTurn[] {
    return this.quizTurns.get(sessionId) || []
  }
  
  /**
   * Get performance metrics
   */
  static getPerformanceMetrics(): PerformanceMetrics {
    const now = new Date().toISOString()
    const activeSessions = Array.from(this.sessions.values()).filter(s => s.isActive)
    const allChatInteractions = Array.from(this.chatInteractions.values()).flat()
    const allQuizTurns = Array.from(this.quizTurns.values()).flat()
    
    // Calculate response times
    const chatTimes = allChatInteractions.map(i => i.processingTime).filter(t => t > 0)
    const quizTimes = allQuizTurns.map(t => t.processingTime).filter(t => t > 0)
    
    // Calculate tool usage
    const toolUsage: Record<string, { calls: number, avgTime: number, errorRate: number }> = {}
    
    allChatInteractions.forEach(interaction => {
      interaction.toolsUsed.forEach(tool => {
        if (!toolUsage[tool]) {
          toolUsage[tool] = { calls: 0, avgTime: 0, errorRate: 0 }
        }
        toolUsage[tool].calls++
        toolUsage[tool].avgTime = (toolUsage[tool].avgTime * (toolUsage[tool].calls - 1) + interaction.processingTime) / toolUsage[tool].calls
        if (interaction.error) {
          toolUsage[tool].errorRate++
        }
      })
    })
    
    // Calculate quiz stats
    const correctAnswers = allQuizTurns.filter(t => t.isCorrect).length
    const totalAnswers = allQuizTurns.length
    const categoryStats: Record<string, number> = {}
    
    allQuizTurns.forEach(turn => {
      categoryStats[turn.category] = (categoryStats[turn.category] || 0) + 1
    })
    
    return {
      timestamp: now,
      sessionCount: this.sessions.size,
      activeUsers: activeSessions.length,
      totalInteractions: allChatInteractions.length + allQuizTurns.length,
      
      avgResponseTime: {
        chat: chatTimes.length > 0 ? Math.round(chatTimes.reduce((a, b) => a + b, 0) / chatTimes.length) : 0,
        quiz: quizTimes.length > 0 ? Math.round(quizTimes.reduce((a, b) => a + b, 0) / quizTimes.length) : 0,
        exa: 0, // TODO: Add specific Exa timing
        mcp: 0  // TODO: Add specific MCP timing
      },
      
      successRates: {
        chat: allChatInteractions.length > 0 ? Math.round((allChatInteractions.filter(i => !i.error).length / allChatInteractions.length) * 100) / 100 : 1,
        quiz: allQuizTurns.length > 0 ? Math.round((allQuizTurns.filter(t => !t.error).length / allQuizTurns.length) * 100) / 100 : 1,
        exa: 1, // TODO: Add specific Exa success rate
        mcp: 1  // TODO: Add specific MCP success rate
      },
      
      toolUsage,
      
      cacheStats: {
        hitRate: 0, // TODO: Integrate with quiz cache
        totalHits: 0,
        totalMisses: 0,
        avgGenerationTime: 0
      },
      
      quizStats: {
        avgCorrectRate: totalAnswers > 0 ? Math.round((correctAnswers / totalAnswers) * 100) / 100 : 0,
        popularCategories: categoryStats,
        difficultyDistribution: {} // TODO: Add difficulty tracking
      }
    }
  }
  
  /**
   * Cleanup inactive sessions (run periodically)
   */
  static cleanupInactiveSessions(maxAgeHours: number = 24): number {
    const cutoffTime = new Date(Date.now() - maxAgeHours * 60 * 60 * 1000)
    let cleanedCount = 0
    
    for (const [sessionId, session] of Array.from(this.sessions.entries())) {
      if (new Date(session.lastActivity) < cutoffTime) {
        this.sessions.delete(sessionId)
        this.chatInteractions.delete(sessionId)
        this.quizSessions.delete(sessionId)
        this.quizTurns.delete(sessionId)
        cleanedCount++
      }
    }
    
    console.log(`[Monitor] Cleaned up ${cleanedCount} inactive sessions older than ${maxAgeHours} hours`)
    return cleanedCount
  }
  
  /**
   * Mark session as inactive
   */
  static markSessionInactive(sessionId: string): void {
    const session = this.sessions.get(sessionId)
    if (session) {
      session.isActive = false
      this.sessions.set(sessionId, session)
    }
  }
  
  /**
   * Get session statistics
   */
  static getSessionStats() {
    const sessions = Array.from(this.sessions.values())
    const activeSessions = sessions.filter(s => s.isActive)
    
    return {
      total: sessions.length,
      active: activeSessions.length,
      chat: sessions.filter(s => s.mode === 'chat').length,
      quiz: sessions.filter(s => s.mode === 'quiz').length,
      mixed: sessions.filter(s => s.mode === 'mixed').length,
      totalInteractions: sessions.reduce((sum, s) => sum + s.totalInteractions, 0)
    }
  }
}