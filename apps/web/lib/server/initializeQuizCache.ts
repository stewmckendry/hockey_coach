/**
 * Initialize Quiz Cache on Server Startup
 * Preloads questions for common categories to ensure fast response times
 */

import { dynamicQuizGenerator } from './dynamicQuizGenerator'

let initialized = false

export async function initializeQuizCache() {
  if (initialized) {
    console.log('[Quiz Cache] Already initialized, skipping...')
    return
  }

  console.log('[Quiz Cache] Starting initialization...')
  
  try {
    // Don't block server startup - run in background
    setTimeout(async () => {
      try {
        await dynamicQuizGenerator.preloadQuestions()
        console.log('[Quiz Cache] Initialization complete')
      } catch (error) {
        console.error('[Quiz Cache] Initialization failed:', error)
        // Non-critical error - app can still function with static questions
      }
    }, 5000) // Wait 5 seconds after server start
    
    initialized = true
  } catch (error) {
    console.error('[Quiz Cache] Failed to schedule initialization:', error)
  }
}

// Auto-initialize when module is imported
if (process.env.NODE_ENV !== 'test') {
  initializeQuizCache()
}