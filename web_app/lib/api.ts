import type { MCPRequest, MCPResponse, MCPHealthResponse, ApiError } from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'

/**
 * API client for communicating with the MCP server
 */
class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  /**
   * Make a request to the MCP server
   */
  async callMCPTool(tool: string, arguments_: Record<string, any>): Promise<any> {
    const request: MCPRequest = {
      tool,
      arguments: arguments_
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/mcp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // TODO: Add authentication headers when available
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new ApiError(
          errorData.error || `HTTP ${response.status}: ${response.statusText}`,
          response.status
        )
      }

      const data: MCPResponse = await response.json()
      
      if (!data.success) {
        throw new ApiError(data.error || 'MCP server returned an error')
      }

      return data.data

    } catch (error) {
      if (error instanceof ApiError) {
        throw error
      }

      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new ApiError('Network error: Unable to connect to the server')
      }

      throw new ApiError(`Unexpected error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  /**
   * Search hockey knowledge
   */
  async searchHockeyKnowledge(
    query: string, 
    maxResults: number = 8
  ): Promise<any> {
    return this.callMCPTool('search_hockey_knowledge', {
      query,
      max_results: maxResults
    })
  }

  /**
   * Get coaching recommendations
   */
  async getCoachingRecommendations(
    situation: string,
    context: Record<string, any> = {}
  ): Promise<any> {
    return this.callMCPTool('get_coaching_recommendations', {
      situation,
      context
    })
  }

  /**
   * Create a practice plan
   */
  async createPracticePlan(
    ageGroup: string,
    durationMinutes: number,
    skillFocusAreas: Array<{ skill: string; time_minutes: number }>,
    practiceContext: string = '',
    includeDryland: boolean = false
  ): Promise<any> {
    return this.callMCPTool('create_practice_plan', {
      age_group: ageGroup,
      duration_minutes: durationMinutes,
      skill_focus_areas: skillFocusAreas,
      practice_context: practiceContext,
      include_dryland: includeDryland
    })
  }

  /**
   * Analyze player development
   */
  async analyzePlayerDevelopment(
    playerPosition: string,
    targetSkills: string[],
    timelineWeeks: number = 8
  ): Promise<any> {
    return this.callMCPTool('analyze_player_development', {
      player_position: playerPosition,
      target_skills: targetSkills,
      timeline_weeks: timelineWeeks
    })
  }

  /**
   * Check API health
   */
  async checkHealth(): Promise<MCPHealthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/mcp`, {
        method: 'GET',
      })

      return await response.json()

    } catch (error) {
      return {
        status: 'unhealthy',
        mcpServer: {
          url: 'unknown',
          error: error instanceof Error ? error.message : 'Unknown error'
        },
        timestamp: new Date().toISOString()
      }
    }
  }

  /**
   * Process natural language queries into specific MCP tool calls
   */
  async processNaturalLanguageQuery(query: string): Promise<any> {
    const lowercaseQuery = query.toLowerCase()

    // Practice planning keywords
    if (lowercaseQuery.includes('practice') || lowercaseQuery.includes('session')) {
      // Try to extract age group and duration
      const ageMatch = query.match(/u(\d+)|under.?(\d+)|(\d+).?(year|yr)/i)
      const durationMatch = query.match(/(\d+).?(min|minute|hour|hr)/i)
      
      let ageGroup = 'U14' // default
      let duration = 90 // default

      if (ageMatch) {
        const age = ageMatch[1] || ageMatch[2] || ageMatch[3]
        ageGroup = `U${age}`
      }

      if (durationMatch) {
        const time = parseInt(durationMatch[1])
        duration = durationMatch[2].startsWith('h') ? time * 60 : time
      }

      // Extract skills mentioned
      const skills = this.extractSkillsFromQuery(query)
      const skillFocusAreas = skills.map(skill => ({
        skill,
        time_minutes: Math.floor(duration * 0.6 / skills.length) // 60% of practice time
      }))

      return this.createPracticePlan(ageGroup, duration, skillFocusAreas, query)
    }

    // Player development keywords
    if (lowercaseQuery.includes('development') || lowercaseQuery.includes('improve') || lowercaseQuery.includes('training plan')) {
      const position = this.extractPositionFromQuery(query) || 'forward'
      const skills = this.extractSkillsFromQuery(query)
      const timelineMatch = query.match(/(\d+).?(week|month)/i)
      
      let timeline = 8 // default weeks
      if (timelineMatch) {
        const time = parseInt(timelineMatch[1])
        timeline = timelineMatch[2].startsWith('m') ? time * 4 : time
      }

      return this.analyzePlayerDevelopment(position, skills, timeline)
    }

    // Coaching advice keywords
    if (lowercaseQuery.includes('advice') || lowercaseQuery.includes('help') || lowercaseQuery.includes('how to')) {
      return this.getCoachingRecommendations(query)
    }

    // Default to knowledge search
    return this.searchHockeyKnowledge(query)
  }

  /**
   * Extract hockey skills from natural language query
   */
  private extractSkillsFromQuery(query: string): string[] {
    const skillMap: Record<string, string> = {
      'skating': 'skating',
      'shooting': 'shooting',
      'passing': 'passing',
      'stickhandling': 'puck handling',
      'checking': 'checking',
      'defensive': 'defensive positioning',
      'offensive': 'offensive play',
      'powerplay': 'power play',
      'penalty': 'penalty kill',
      'faceoff': 'faceoffs',
      'breakout': 'breakout',
      'forecheck': 'forechecking',
      'backcheck': 'backchecking'
    }

    const lowercaseQuery = query.toLowerCase()
    const foundSkills: string[] = []

    Object.entries(skillMap).forEach(([keyword, skill]) => {
      if (lowercaseQuery.includes(keyword)) {
        foundSkills.push(skill)
      }
    })

    return foundSkills.length > 0 ? foundSkills : ['skating', 'puck handling'] // defaults
  }

  /**
   * Extract player position from natural language query
   */
  private extractPositionFromQuery(query: string): string | null {
    const positions = ['forward', 'defenseman', 'defense', 'goalie', 'goalkeeper']
    const lowercaseQuery = query.toLowerCase()

    for (const position of positions) {
      if (lowercaseQuery.includes(position)) {
        return position === 'defense' ? 'defenseman' : position
      }
    }

    return null
  }
}

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  public status?: number
  public code?: string

  constructor(message: string, status?: number, code?: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

// Create singleton instance
export const apiClient = new ApiClient()

// Export individual methods for convenience
export const {
  searchHockeyKnowledge,
  getCoachingRecommendations,
  createPracticePlan,
  analyzePlayerDevelopment,
  processNaturalLanguageQuery,
  checkHealth
} = apiClient
