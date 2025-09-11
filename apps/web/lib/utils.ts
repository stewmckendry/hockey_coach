import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import type { ConversationThread } from './types'

/**
 * Utility function to merge Tailwind CSS classes
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Generate a unique ID for chat messages
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Format timestamp for display
 */
export function formatTimestamp(date: Date | string): string {
  // Handle both Date objects and date strings from localStorage
  const dateObj = typeof date === 'string' ? new Date(date) : date
  
  // Check if the date is valid
  if (!dateObj || isNaN(dateObj.getTime())) {
    return 'Unknown time'
  }
  
  const now = new Date()
  const diff = now.getTime() - dateObj.getTime()
  const minutes = Math.floor(diff / 60000)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  
  return dateObj.toLocaleDateString()
}

/**
 * Deserialize conversation data from localStorage, converting date strings back to Date objects
 */
export function deserializeConversations(conversations: any[]): ConversationThread[] {
  return conversations.map(conv => ({
    ...conv,
    createdAt: new Date(conv.createdAt),
    updatedAt: new Date(conv.updatedAt),
    messages: conv.messages?.map((msg: any) => ({
      ...msg,
      timestamp: new Date(msg.timestamp)
    })) || []
  }))
}

/**
 * Truncate text to specified length
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength).trim() + '...'
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Debounce function to limit API calls
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
}

/**
 * Sleep utility for delays
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Check if code is running in browser
 */
export function isBrowser(): boolean {
  return typeof window !== 'undefined'
}

/**
 * Local storage helpers with error handling
 */
export const storage = {
  get<T>(key: string, defaultValue: T): T {
    if (!isBrowser()) return defaultValue
    
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : defaultValue
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error)
      return defaultValue
    }
  },

  set<T>(key: string, value: T): void {
    if (!isBrowser()) return
    
    try {
      window.localStorage.setItem(key, JSON.stringify(value))
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error)
    }
  },

  remove(key: string): void {
    if (!isBrowser()) return
    
    try {
      window.localStorage.removeItem(key)
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error)
    }
  }
}

/**
 * Format duration in minutes to readable string
 */
export function formatDuration(minutes: number): string {
  if (minutes < 60) return `${minutes}min`
  
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  
  if (remainingMinutes === 0) return `${hours}h`
  return `${hours}h ${remainingMinutes}min`
}

/**
 * Parse hockey age group to get numeric values
 */
export function parseAgeGroup(ageGroup: string): { min: number; max: number } | null {
  const match = ageGroup.match(/U(\d+)|(\d+)-(\d+)/)
  
  if (!match) return null
  
  if (match[1]) {
    // U14 format
    const age = parseInt(match[1])
    return { min: age - 2, max: age }
  }
  
  if (match[2] && match[3]) {
    // 14-16 format
    return { min: parseInt(match[2]), max: parseInt(match[3]) }
  }
  
  return null
}

/**
 * Capitalize first letter of each word
 */
export function titleCase(str: string): string {
  return str.replace(/\w\S*/g, (txt) => 
    txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
  )
}

/**
 * Extract hockey skill keywords from text
 */
export function extractHockeySkills(text: string): string[] {
  const skills = [
    'skating', 'shooting', 'passing', 'stickhandling', 'checking',
    'positioning', 'breakout', 'forecheck', 'backcheck', 'powerplay',
    'penalty kill', 'faceoff', 'defensive zone', 'offensive zone',
    'neutral zone', 'cycling', 'screening', 'rebound', 'one-timer',
    'crossover', 'backwards skating', 'pivoting', 'acceleration',
    'puck protection', 'board play', 'net drive', 'gap control'
  ]
  
  const lowerText = text.toLowerCase()
  return skills.filter(skill => lowerText.includes(skill))
}
