/**
 * Hockey IQ Monitor Storage
 * 
 * Handles persistent storage for monitoring data using file-based JSON storage.
 * This can be upgraded to SQLite or other database later.
 */

import fs from 'fs'
import path from 'path'
import { SessionLog, ChatInteraction, QuizSession, QuizTurn } from '@/lib/types/monitoring'

class MonitorStorage {
  private readonly storageDir: string
  private readonly sessionsFile: string
  private readonly chatFile: string
  private readonly quizSessionsFile: string
  private readonly quizTurnsFile: string
  
  constructor() {
    this.storageDir = path.join(process.cwd(), 'data', 'monitor')
    this.sessionsFile = path.join(this.storageDir, 'sessions.json')
    this.chatFile = path.join(this.storageDir, 'chat-interactions.json')
    this.quizSessionsFile = path.join(this.storageDir, 'quiz-sessions.json')
    this.quizTurnsFile = path.join(this.storageDir, 'quiz-turns.json')
    
    this.ensureStorageDirectory()
  }
  
  /**
   * Ensure storage directory exists
   */
  private ensureStorageDirectory(): void {
    try {
      if (!fs.existsSync(this.storageDir)) {
        fs.mkdirSync(this.storageDir, { recursive: true })
        console.log(`[MonitorStorage] Created storage directory: ${this.storageDir}`)
      }
    } catch (error) {
      console.error(`[MonitorStorage] Failed to create storage directory:`, error)
    }
  }
  
  /**
   * Load data from file with error handling
   */
  private loadFromFile<T>(filePath: string, defaultValue: T): T {
    try {
      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf8')
        return JSON.parse(content)
      }
    } catch (error) {
      console.error(`[MonitorStorage] Failed to load from ${filePath}:`, error)
    }
    return defaultValue
  }
  
  /**
   * Save data to file with error handling
   */
  private saveToFile<T>(filePath: string, data: T): void {
    try {
      fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8')
    } catch (error) {
      console.error(`[MonitorStorage] Failed to save to ${filePath}:`, error)
    }
  }
  
  /**
   * Append to daily log file
   */
  private appendToLogFile(filename: string, data: any): void {
    try {
      const today = new Date().toISOString().split('T')[0]
      const logFile = path.join(this.storageDir, 'logs', `${filename}-${today}.json`)
      
      // Ensure logs directory exists
      const logsDir = path.dirname(logFile)
      if (!fs.existsSync(logsDir)) {
        fs.mkdirSync(logsDir, { recursive: true })
      }
      
      const logEntry = {
        timestamp: new Date().toISOString(),
        ...data
      }
      
      fs.appendFileSync(logFile, JSON.stringify(logEntry) + '\n', 'utf8')
    } catch (error) {
      console.error(`[MonitorStorage] Failed to append to log file:`, error)
    }
  }
  
  // Session Management
  
  /**
   * Load all sessions
   */
  loadSessions(): Record<string, SessionLog> {
    const sessions = this.loadFromFile(this.sessionsFile, {})
    return sessions
  }
  
  /**
   * Save all sessions
   */
  saveSessions(sessions: Record<string, SessionLog>): void {
    this.saveToFile(this.sessionsFile, sessions)
  }
  
  /**
   * Save individual session and log to daily file
   */
  saveSession(session: SessionLog): void {
    const sessions = this.loadSessions()
    sessions[session.sessionId] = session
    this.saveSessions(sessions)
    
    // Also append to daily log
    this.appendToLogFile('sessions', session)
  }
  
  // Chat Interactions
  
  /**
   * Load chat interactions
   */
  loadChatInteractions(): Record<string, ChatInteraction[]> {
    return this.loadFromFile(this.chatFile, {})
  }
  
  /**
   * Save chat interactions
   */
  saveChatInteractions(interactions: Record<string, ChatInteraction[]>): void {
    this.saveToFile(this.chatFile, interactions)
  }
  
  /**
   * Add chat interaction
   */
  addChatInteraction(interaction: ChatInteraction): void {
    const interactions = this.loadChatInteractions()
    if (!interactions[interaction.sessionId]) {
      interactions[interaction.sessionId] = []
    }
    interactions[interaction.sessionId].push(interaction)
    this.saveChatInteractions(interactions)
    
    // Also append to daily log
    this.appendToLogFile('chat', interaction)
  }
  
  // Quiz Sessions
  
  /**
   * Load quiz sessions
   */
  loadQuizSessions(): Record<string, QuizSession> {
    return this.loadFromFile(this.quizSessionsFile, {})
  }
  
  /**
   * Save quiz sessions
   */
  saveQuizSessions(sessions: Record<string, QuizSession>): void {
    this.saveToFile(this.quizSessionsFile, sessions)
  }
  
  /**
   * Save individual quiz session
   */
  saveQuizSession(session: QuizSession): void {
    const sessions = this.loadQuizSessions()
    sessions[session.sessionId] = session
    this.saveQuizSessions(sessions)
    
    // Also append to daily log
    this.appendToLogFile('quiz-sessions', session)
  }
  
  // Quiz Turns
  
  /**
   * Load quiz turns
   */
  loadQuizTurns(): Record<string, QuizTurn[]> {
    return this.loadFromFile(this.quizTurnsFile, {})
  }
  
  /**
   * Save quiz turns
   */
  saveQuizTurns(turns: Record<string, QuizTurn[]>): void {
    this.saveToFile(this.quizTurnsFile, turns)
  }
  
  /**
   * Add quiz turn
   */
  addQuizTurn(turn: QuizTurn): void {
    const turns = this.loadQuizTurns()
    if (!turns[turn.sessionId]) {
      turns[turn.sessionId] = []
    }
    turns[turn.sessionId].push(turn)
    this.saveQuizTurns(turns)
    
    // Also append to daily log
    this.appendToLogFile('quiz-turns', turn)
  }
  
  // Maintenance
  
  /**
   * Clean up old data
   */
  cleanup(retentionDays: number = 7): number {
    let cleanedCount = 0
    const cutoffDate = new Date(Date.now() - retentionDays * 24 * 60 * 60 * 1000)
    
    try {
      // Clean up sessions
      const sessions = this.loadSessions()
      const originalSessionCount = Object.keys(sessions).length
      
      Object.keys(sessions).forEach(sessionId => {
        if (new Date(sessions[sessionId].lastActivity) < cutoffDate) {
          delete sessions[sessionId]
          cleanedCount++
        }
      })
      
      if (cleanedCount > 0) {
        this.saveSessions(sessions)
        
        // Clean up related chat interactions
        const chatInteractions = this.loadChatInteractions()
        Object.keys(chatInteractions).forEach(sessionId => {
          if (!sessions[sessionId]) {
            delete chatInteractions[sessionId]
          }
        })
        this.saveChatInteractions(chatInteractions)
        
        // Clean up related quiz data
        const quizSessions = this.loadQuizSessions()
        const quizTurns = this.loadQuizTurns()
        
        Object.keys(quizSessions).forEach(sessionId => {
          if (!sessions[sessionId]) {
            delete quizSessions[sessionId]
          }
        })
        
        Object.keys(quizTurns).forEach(sessionId => {
          if (!sessions[sessionId]) {
            delete quizTurns[sessionId]
          }
        })
        
        this.saveQuizSessions(quizSessions)
        this.saveQuizTurns(quizTurns)
      }
      
      // Clean up old log files
      const logsDir = path.join(this.storageDir, 'logs')
      if (fs.existsSync(logsDir)) {
        const logFiles = fs.readdirSync(logsDir)
        logFiles.forEach(file => {
          const filePath = path.join(logsDir, file)
          const stat = fs.statSync(filePath)
          if (stat.mtime < cutoffDate) {
            fs.unlinkSync(filePath)
            console.log(`[MonitorStorage] Cleaned up old log file: ${file}`)
          }
        })
      }
      
    } catch (error) {
      console.error(`[MonitorStorage] Cleanup failed:`, error)
    }
    
    return cleanedCount
  }
  
  /**
   * Get storage statistics
   */
  getStorageStats() {
    try {
      const sessions = this.loadSessions()
      const chatInteractions = this.loadChatInteractions()
      const quizSessions = this.loadQuizSessions()
      const quizTurns = this.loadQuizTurns()
      
      const totalChatInteractions = Object.values(chatInteractions)
        .reduce((sum, interactions) => sum + interactions.length, 0)
      
      const totalQuizTurns = Object.values(quizTurns)
        .reduce((sum, turns) => sum + turns.length, 0)
      
      return {
        sessions: Object.keys(sessions).length,
        chatInteractions: totalChatInteractions,
        quizSessions: Object.keys(quizSessions).length,
        quizTurns: totalQuizTurns,
        storageDir: this.storageDir,
        lastCleanup: new Date().toISOString()
      }
    } catch (error) {
      console.error(`[MonitorStorage] Failed to get storage stats:`, error)
      return null
    }
  }
  
  /**
   * Export data for analysis
   */
  exportData(dateRange?: { start: string, end: string }) {
    try {
      const sessions = this.loadSessions()
      const chatInteractions = this.loadChatInteractions()
      const quizSessions = this.loadQuizSessions()
      const quizTurns = this.loadQuizTurns()
      
      // Filter by date range if provided
      let filteredData = {
        sessions,
        chatInteractions,
        quizSessions,
        quizTurns
      }
      
      if (dateRange) {
        const startDate = new Date(dateRange.start)
        const endDate = new Date(dateRange.end)
        
        // Filter sessions
        const filteredSessions: Record<string, SessionLog> = {}
        Object.entries(sessions).forEach(([sessionId, session]) => {
          const sessionDate = new Date(session.startTime)
          if (sessionDate >= startDate && sessionDate <= endDate) {
            filteredSessions[sessionId] = session
          }
        })
        
        // Filter related data based on filtered sessions
        const sessionIds = new Set(Object.keys(filteredSessions))
        
        const filteredChatInteractions: Record<string, ChatInteraction[]> = {}
        Object.entries(chatInteractions).forEach(([sessionId, interactions]) => {
          if (sessionIds.has(sessionId)) {
            filteredChatInteractions[sessionId] = interactions
          }
        })
        
        const filteredQuizSessions: Record<string, QuizSession> = {}
        Object.entries(quizSessions).forEach(([sessionId, session]) => {
          if (sessionIds.has(sessionId)) {
            filteredQuizSessions[sessionId] = session
          }
        })
        
        const filteredQuizTurns: Record<string, QuizTurn[]> = {}
        Object.entries(quizTurns).forEach(([sessionId, turns]) => {
          if (sessionIds.has(sessionId)) {
            filteredQuizTurns[sessionId] = turns
          }
        })
        
        filteredData = {
          sessions: filteredSessions,
          chatInteractions: filteredChatInteractions,
          quizSessions: filteredQuizSessions,
          quizTurns: filteredQuizTurns
        }
      }
      
      return {
        exportDate: new Date().toISOString(),
        dateRange,
        data: filteredData,
        stats: {
          sessions: Object.keys(filteredData.sessions).length,
          chatInteractions: Object.values(filteredData.chatInteractions).reduce((sum, interactions) => sum + interactions.length, 0),
          quizSessions: Object.keys(filteredData.quizSessions).length,
          quizTurns: Object.values(filteredData.quizTurns).reduce((sum, turns) => sum + turns.length, 0)
        }
      }
    } catch (error) {
      console.error(`[MonitorStorage] Export failed:`, error)
      return null
    }
  }
}

// Export singleton instance
export const monitorStorage = new MonitorStorage()