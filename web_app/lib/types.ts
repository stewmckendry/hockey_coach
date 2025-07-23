// ============================================================================
// Chat Message Types
// ============================================================================

export interface ChatMessage {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  metadata?: {
    tool?: string
    processingTime?: number
    error?: string
  }
}

export interface ChatState {
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  isTyping: boolean
}

// ============================================================================
// MCP API Types
// ============================================================================

export interface MCPRequest {
  tool: string
  parameters: Record<string, any>
}

export interface MCPResponse {
  success: boolean
  data: any
  timestamp: string
  error?: string
}

export interface MCPHealthResponse {
  status: 'healthy' | 'unhealthy'
  mcpServer: {
    url: string
    status?: number
    error?: string
  }
  timestamp: string
}

// ============================================================================
// Hockey Domain Types (from MCP server)
// ============================================================================

export interface HockeyKnowledgeResult {
  id: string
  title: string
  content_type: 'drill' | 'video' | 'skill' | 'tactic' | 'rule' | 'dryland' | 'interview'
  summary: string
  complexity: 'beginner' | 'intermediate' | 'advanced'
  source: string
  age_recommendation?: string
  equipment?: string
  teaching_points?: string
  skills_practiced?: string
  positions?: string
  url?: string
  metadata?: Record<string, any>
}

export interface CoachingRecommendation {
  recommendation: string
  rationale: string
  priority: 'high' | 'medium' | 'low'
  category: string
  supporting_evidence: HockeyKnowledgeResult[]
}

export interface PracticeActivity {
  activity: string
  duration: string
  skill_focus?: string
  description: string
  source_type?: string
  teaching_points?: string
  setup?: string
}

export interface CoachingPlan {
  title: string
  age_group: string
  duration_minutes: number
  focus_areas: string[]
  warmup: PracticeActivity[]
  main_activities: PracticeActivity[]
  cooldown: PracticeActivity[]
  equipment_needed: string[]
  coaching_notes: string
}

export interface PlayerDevelopmentPlan {
  player_name: string
  position: string
  current_level: string
  target_skills: string[]
  recommended_drills: string[]
  dryland_exercises: string[]
  timeline_weeks: number
  progress_markers: string[]
}

// ============================================================================
// UI Component Types
// ============================================================================

export interface ButtonProps {
  children: React.ReactNode
  onClick?: () => void
  disabled?: boolean
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  className?: string
  type?: 'button' | 'submit' | 'reset'
}

export interface CardProps {
  children: React.ReactNode
  className?: string
  onClick?: () => void
}

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

// ============================================================================
// Hook Types
// ============================================================================

export interface UseChatReturn {
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  isTyping: boolean
  sendMessage: (content: string) => Promise<void>
  clearMessages: () => void
  retry: () => Promise<void>
}

export interface UseLocalStorageReturn<T> {
  value: T
  setValue: (value: T | ((prev: T) => T)) => void
  removeValue: () => void
}

// ============================================================================
// Utility Types
// ============================================================================

export type ApiError = {
  message: string
  status?: number
  code?: string
}

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

// ============================================================================
// Example Data Types
// ============================================================================

export interface QuickStartExample {
  title: string
  description: string
  prompt: string
  category: 'practice' | 'development' | 'knowledge' | 'season'
  icon: string
}
