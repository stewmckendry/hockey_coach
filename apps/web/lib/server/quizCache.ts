/**
 * Quiz Cache Service
 * Implements intelligent caching for dynamically generated quiz questions
 * with TTL (Time To Live) and category-based storage
 */

// Define Question type locally to avoid circular dependencies
interface Question {
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
}

interface CachedQuestion extends Question {
  generatedAt: number
  expiresAt: number
}

interface CacheEntry {
  questions: CachedQuestion[]
  lastUpdated: number
}

class QuizCacheService {
  private cache: Map<string, CacheEntry> = new Map()
  private readonly TTL = 2 * 60 * 60 * 1000 // 2 hours in milliseconds
  private readonly MAX_QUESTIONS_PER_CATEGORY = 20
  private readonly MIN_CACHE_SIZE = 5 // Minimum questions to keep cached
  
  constructor() {
    // Start background cleanup task
    this.startCleanupTask()
  }

  /**
   * Get a question from cache or return null if none available
   */
  getQuestion(category: string): CachedQuestion | null {
    const entry = this.cache.get(category)
    
    if (!entry || entry.questions.length === 0) {
      return null
    }

    // Filter out expired questions
    const validQuestions = entry.questions.filter(q => 
      q.expiresAt > Date.now()
    )

    if (validQuestions.length === 0) {
      return null
    }

    // Return random valid question
    const randomIndex = Math.floor(Math.random() * validQuestions.length)
    return validQuestions[randomIndex]
  }

  /**
   * Get a question from cache that hasn't been asked yet
   * Returns null if all cached questions have been asked
   */
  getUniqueQuestion(category: string, askedQuestionIds: string[]): CachedQuestion | null {
    const entry = this.cache.get(category)
    
    if (!entry || entry.questions.length === 0) {
      console.log(`[QuizCache] No questions in cache for category: ${category}`)
      return null
    }

    // Filter out expired and already asked questions
    const validQuestions = entry.questions.filter(q => 
      q.expiresAt > Date.now() && !askedQuestionIds.includes(q.id)
    )

    if (validQuestions.length === 0) {
      console.log(`[QuizCache] All cached questions for ${category} have been asked or expired`)
      return null
    }

    // Return random valid unasked question
    const randomIndex = Math.floor(Math.random() * validQuestions.length)
    console.log(`[QuizCache] Found ${validQuestions.length} unasked questions for ${category}`)
    return validQuestions[randomIndex]
  }

  /**
   * Add a question to the cache
   */
  addQuestion(category: string, question: Question, thunderContext?: string, researchSource?: string): void {
    const now = Date.now()
    const cachedQuestion: CachedQuestion = {
      ...question,
      generatedAt: now,
      expiresAt: now + this.TTL,
      thunderContext,
      researchSource
    }

    const entry = this.cache.get(category) || { questions: [], lastUpdated: now }
    
    // Add new question
    entry.questions.push(cachedQuestion)
    
    // Maintain max cache size per category
    if (entry.questions.length > this.MAX_QUESTIONS_PER_CATEGORY) {
      // Remove oldest expired questions first
      entry.questions = entry.questions
        .filter(q => q.expiresAt > now)
        .sort((a, b) => b.generatedAt - a.generatedAt)
        .slice(0, this.MAX_QUESTIONS_PER_CATEGORY)
    }
    
    entry.lastUpdated = now
    this.cache.set(category, entry)
  }

  /**
   * Check if category needs more questions
   */
  needsQuestions(category: string): boolean {
    const entry = this.cache.get(category)
    
    if (!entry) {
      return true
    }

    const validQuestions = entry.questions.filter(q => 
      q.expiresAt > Date.now()
    )

    return validQuestions.length < this.MIN_CACHE_SIZE
  }

  /**
   * Get cache statistics for monitoring
   */
  getStats() {
    const stats: Record<string, any> = {}
    
    for (const [category, entry] of Array.from(this.cache.entries())) {
      const validQuestions = entry.questions.filter((q: CachedQuestion) => 
        q.expiresAt > Date.now()
      )
      
      stats[category] = {
        total: entry.questions.length,
        valid: validQuestions.length,
        expired: entry.questions.length - validQuestions.length,
        lastUpdated: new Date(entry.lastUpdated).toISOString()
      }
    }
    
    return stats
  }

  /**
   * Preload questions for common categories
   */
  async preloadCategories(categories: string[], generateFn: (cat: string) => Promise<Question>): Promise<void> {
    const preloadPromises = categories.map(async (category) => {
      if (this.needsQuestions(category)) {
        try {
          // Generate 5 questions per category for preloading
          for (let i = 0; i < 5; i++) {
            const question = await generateFn(category)
            this.addQuestion(category, question)
          }
        } catch (error) {
          console.error(`Failed to preload category ${category}:`, error)
        }
      }
    })

    await Promise.all(preloadPromises)
  }

  /**
   * Clear expired questions periodically
   */
  private startCleanupTask(): void {
    setInterval(() => {
      const now = Date.now()
      
      for (const [category, entry] of Array.from(this.cache.entries())) {
        const validQuestions = entry.questions.filter((q: CachedQuestion) => 
          q.expiresAt > now
        )
        
        if (validQuestions.length !== entry.questions.length) {
          entry.questions = validQuestions
          entry.lastUpdated = now
          
          // Remove category if no valid questions
          if (validQuestions.length === 0) {
            this.cache.delete(category)
          }
        }
      }
    }, 30 * 60 * 1000) // Clean up every 30 minutes
  }

  /**
   * Force clear all cache
   */
  clearCache(): void {
    this.cache.clear()
  }

  /**
   * Clear cache for specific category
   */
  clearCategory(category: string): void {
    this.cache.delete(category)
  }
}

// Export singleton instance
export const quizCache = new QuizCacheService()