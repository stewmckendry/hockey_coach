/**
 * Hockey IQ Monitoring System Types
 * 
 * Defines interfaces for session tracking, chat/quiz logging,
 * and performance monitoring for the Hockey IQ Chatbot.
 */

export interface SessionLog {
  sessionId: string
  ipAddress: string
  userAgent: string
  startTime: string
  lastActivity: string
  mode: 'chat' | 'quiz' | 'mixed'
  totalInteractions: number
  isActive: boolean
}

export interface ChatInteraction {
  sessionId: string
  messageId: string
  timestamp: string
  question: string
  response: string
  toolsUsed: string[]
  processingTime: number
  responseId: string // OpenAI Responses API ID for investigation
  category?: string
  ageGroup: string
  mode: 'qa' | 'socratic'
  error?: string
}

export interface QuizQuestion {
  id: string
  category: string
  level: string
  question: string
  correctAnswer: string
  hints: string[]
  followUpQuestions: string[]
  encouragementMessages: {
    correct: string
    incorrect: string
  }
  funFact: string
  thunderContext?: string
  researchSource?: string
  type: 'static' | 'dynamic'
  generatedAt?: string
  cacheHit?: boolean
}

export interface QuizSession {
  sessionId: string
  startTime: string
  lastActivity: string
  questionBank: QuizQuestion[]
  questionsAsked: string[] // Question IDs that have been asked
  questionsRemaining: string[] // Question IDs not yet asked
  currentQuestionIndex: number
  userScore: {
    correct: number
    total: number
    streak: number
    longestStreak: number
  }
  categoryStats: Record<string, {
    correct: number
    total: number
    averageTime: number
  }>
  regenerationThreshold: number // Number of questions before regenerating bank
  difficulty: 'rookie' | 'player' | 'allstar'
  preferences: {
    includeThunderContext: boolean
    preferredCategories: string[]
  }
}

export interface QuizTurn {
  sessionId: string
  turnId: string
  timestamp: string
  questionId: string
  question: string
  questionType: 'static' | 'dynamic'
  category: string
  difficulty: string
  researchSource: string
  userAnswer: string
  aiResponse: string
  isCorrect: boolean
  processingTime: number
  hintsUsed: number
  followUpGenerated: boolean
  error?: string
}

export interface PerformanceMetrics {
  timestamp: string
  sessionCount: number
  activeUsers: number
  totalInteractions: number
  
  // Response Times
  avgResponseTime: {
    chat: number
    quiz: number
    exa: number
    mcp: number
  }
  
  // Success Rates
  successRates: {
    chat: number
    quiz: number
    exa: number
    mcp: number
  }
  
  // Tool Usage
  toolUsage: Record<string, {
    calls: number
    avgTime: number
    errorRate: number
  }>
  
  // Cache Performance
  cacheStats: {
    hitRate: number
    totalHits: number
    totalMisses: number
    avgGenerationTime: number
  }
  
  // Quiz Analytics
  quizStats: {
    avgCorrectRate: number
    popularCategories: Record<string, number>
    difficultyDistribution: Record<string, number>
  }
}

export interface MonitoringConfig {
  enableSessionTracking: boolean
  enablePerformanceMetrics: boolean
  logRetentionDays: number
  maxSessionsToStore: number
  performanceMetricsInterval: number // seconds
  enableRealTimeUpdates: boolean
}

// API Response types for monitor endpoints
export interface SessionListResponse {
  success: boolean
  sessions: SessionLog[]
  totalCount: number
  activeCount: number
  timestamp: string
}

export interface ChatHistoryResponse {
  success: boolean
  sessionId: string
  interactions: ChatInteraction[]
  sessionInfo: SessionLog
  totalCount: number
  timestamp: string
}

export interface QuizHistoryResponse {
  success: boolean
  sessionId: string
  session: QuizSession
  turns: QuizTurn[]
  sessionInfo: SessionLog
  timestamp: string
}

export interface MonitorStatsResponse {
  success: boolean
  metrics: PerformanceMetrics
  config: MonitoringConfig
  timestamp: string
}

// Utility types for filtering and searching
export interface MonitorFilters {
  timeRange?: {
    start: string
    end: string
  }
  mode?: 'chat' | 'quiz' | 'mixed'
  minInteractions?: number
  ipAddress?: string
  category?: string
  difficulty?: string
  toolsUsed?: string[]
  correctnessFilter?: 'correct' | 'incorrect' | 'all'
}

export interface SearchOptions {
  query?: string
  filters?: MonitorFilters
  sortBy?: 'timestamp' | 'processingTime' | 'score' | 'interactions'
  sortOrder?: 'asc' | 'desc'
  limit?: number
  offset?: number
}