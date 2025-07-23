import type { MCPRequest, MCPResponse, MCPHealthResponse } from './types'

const BRIDGE_BASE_URL = 'http://localhost:3002'

/**
 * API client for communicating with the MCP server via our backend bridge
 */
class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = BRIDGE_BASE_URL) {
    this.baseUrl = baseUrl
  }

  /**
   * Make a request to the MCP server via our Python bridge
   */
  async callMCPTool(tool: string, parameters: Record<string, any> = {}): Promise<any> {
    const request: MCPRequest = {
      tool,
      parameters
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/mcp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`)
      }

      const data: MCPResponse = await response.json()
      
      if (!data.success) {
        throw new Error(data.error || 'MCP server returned an error')
      }

      return data.data

    } catch (error) {
      console.error('MCP API call failed:', error)
      throw error
    }
  }

  /**
   * Search hockey knowledge across all content types
   */
  async searchHockeyKnowledge(
    query: string, 
    options: {
      content_types?: string[]
      complexity_levels?: string[]
      age_groups?: string[]
      n_results?: number
    } = {}
  ): Promise<any> {
    return this.callMCPTool('search_hockey_knowledge', {
      query,
      ...options
    })
  }

  /**
   * Get coaching recommendations based on team parameters
   */
  async getCoachingRecommendations(
    teamAge: string,
    skillFocus: string,
    availableTime: number,
    teamSize: number,
    equipmentAvailable: string[] = []
  ): Promise<any> {
    return this.callMCPTool('get_coaching_recommendations', {
      team_age: teamAge,
      skill_focus: skillFocus,
      available_time: availableTime,
      team_size: teamSize,
      equipment_available: equipmentAvailable
    })
  }

  /**
   * Create a comprehensive practice plan
   */
  async createPracticePlan(
    ageGroup: string,
    durationMinutes: number,
    skillFocusAreas: Array<{ skill: string; time_minutes: number }>,
    options: {
      number_of_players?: number
      practice_context?: string
      team_systems_focus?: string[]
      include_dryland?: boolean
      equipment_available?: string[]
      coaching_priorities?: string
    } = {}
  ): Promise<any> {
    return this.callMCPTool('create_practice_plan', {
      age_group: ageGroup,
      duration_minutes: durationMinutes,
      skill_focus_areas: skillFocusAreas,
      number_of_players: options.number_of_players || 15,
      practice_context: options.practice_context || '',
      team_systems_focus: options.team_systems_focus,
      include_dryland: options.include_dryland || false,
      equipment_available: options.equipment_available,
      coaching_priorities: options.coaching_priorities
    })
  }

  /**
   * Analyze player development and create individual plans
   */
  async analyzePlayerDevelopment(
    playerPosition: string,
    currentSkills: string[],
    targetSkills: string[],
    timelineWeeks: number = 8
  ): Promise<any> {
    return this.callMCPTool('analyze_player_development', {
      player_position: playerPosition,
      current_skills: currentSkills,
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
    if (lowercaseQuery.includes('practice') || lowercaseQuery.includes('plan')) {
      const ageGroup = this.extractAgeGroupFromQuery(query) || 'U12'
      const duration = this.extractDurationFromQuery(query) || 60
      const skills = this.extractSkillsFromQuery(query)
      
      const skillFocusAreas = skills.map(skill => ({
        skill,
        time_minutes: Math.floor(duration * 0.6 / skills.length) // 60% of practice time
      }))

      return this.createPracticePlan(ageGroup, duration, skillFocusAreas, {
        practice_context: query
      })
    }

    // Player development keywords
    if (lowercaseQuery.includes('development') || lowercaseQuery.includes('improve') || lowercaseQuery.includes('training plan')) {
      const position = this.extractPositionFromQuery(query) || 'forward'
      const targetSkills = this.extractSkillsFromQuery(query)
      const timelineMatch = query.match(/(\d+).?(week|month)/i)
      
      let timeline = 8 // default weeks
      if (timelineMatch) {
        const time = parseInt(timelineMatch[1])
        timeline = timelineMatch[2].startsWith('m') ? time * 4 : time
      }

      return this.analyzePlayerDevelopment(position, [], targetSkills, timeline)
    }

    // Coaching advice keywords
    if (lowercaseQuery.includes('advice') || lowercaseQuery.includes('help') || lowercaseQuery.includes('how to')) {
      const ageGroup = this.extractAgeGroupFromQuery(query) || 'U12'
      const skill = this.extractSkillsFromQuery(query)[0] || 'skating'
      
      return this.getCoachingRecommendations(
        ageGroup,
        skill,
        60, // default 60 minutes
        15, // default team size
        ['pucks', 'cones'] // default equipment
      )
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
      'defense': 'defensive positioning',
      'offense': 'offensive tactics',
      'breakout': 'breakout',
      'forecheck': 'forechecking',
      'powerplay': 'power play',
      'penalty kill': 'penalty kill'
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

  /**
   * Extract age group from natural language query
   */
  private extractAgeGroupFromQuery(query: string): string | null {
    const ageGroups = ['U6', 'U8', 'U10', 'U12', 'U14', 'U16', 'U18', 'bantam', 'midget', 'peewee', 'atom', 'novice']
    const lowercaseQuery = query.toLowerCase()

    for (const ageGroup of ageGroups) {
      if (lowercaseQuery.includes(ageGroup.toLowerCase())) {
        return ageGroup
      }
    }

    // Check for numeric age patterns
    const ageMatch = query.match(/(\d{1,2}).?(year|yr|u)/i)
    if (ageMatch) {
      const age = parseInt(ageMatch[1])
      if (age <= 8) return 'U8'
      if (age <= 10) return 'U10'
      if (age <= 12) return 'U12'
      if (age <= 14) return 'U14'
      if (age <= 16) return 'U16'
      if (age <= 18) return 'U18'
    }

    return null
  }

  /**
   * Extract duration from natural language query
   */
  private extractDurationFromQuery(query: string): number | null {
    const durationMatch = query.match(/(\d+).?(minute|min|hour|hr)/i)
    if (durationMatch) {
      const time = parseInt(durationMatch[1])
      return durationMatch[2].startsWith('h') ? time * 60 : time
    }
    return null
  }
}

// Create and export singleton instance
export const apiClient = new ApiClient()

// Export the class for testing
export { ApiClient }
