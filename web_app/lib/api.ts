import { 
  MCPRequest, 
  MCPResponse, 
  HockeyKnowledgeResult, 
  CoachingRecommendation, 
  CoachingPlan, 
  PlayerDevelopmentPlan 
} from './types'

/**
 * API client for communicating with the FastMCP server
 */
class APIClient {
  private baseUrl: string

  constructor() {
    // Use environment variable or default to localhost
    this.baseUrl = process.env.NEXT_PUBLIC_FASTMCP_URL || 'http://localhost:3001'
  }

  /**
   * Make a secure request to the MCP server
   */
  private async makeRequest<T>(endpoint: string, request: MCPRequest): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data: MCPResponse = await response.json()
      
      if (!data.success) {
        throw new Error(data.error || 'MCP request failed')
      }

      return data.data as T
    } catch (error) {
      console.error('MCP API request failed:', error)
      throw error
    }
  }

  /**
   * Search hockey knowledge base
   */
  async searchHockeyKnowledge(
    query: string, 
    options: {
      content_types?: string[]
      age_groups?: string[]
      n_results?: number
    } = {}
  ): Promise<HockeyKnowledgeResult[]> {
    return this.makeRequest<HockeyKnowledgeResult[]>('/api/mcp', {
      tool: 'search_hockey_knowledge',
      parameters: {
        query,
        content_types: options.content_types || [],
        age_groups: options.age_groups || [],
        n_results: options.n_results || 5
      }
    })
  }

  /**
   * Get coaching recommendations
   */
  async getCoachingRecommendations(
    ageGroup: string,
    skill: string,
    durationMinutes: number,
    teamSize: number,
    equipment: string[]
  ): Promise<CoachingRecommendation[]> {
    return this.makeRequest<CoachingRecommendation[]>('/api/mcp', {
      tool: 'get_coaching_recommendations',
      parameters: {
        age_group: ageGroup,
        skill,
        duration_minutes: durationMinutes,
        team_size: teamSize,
        equipment
      }
    })
  }

  /**
   * Create a practice plan
   */
  async createPracticePlan(
    ageGroup: string,
    durationMinutes: number,
    skills: Array<{ skill: string; time_minutes: number }>,
    options: {
      number_of_players?: number
      practice_context?: string
    } = {}
  ): Promise<CoachingPlan> {
    return this.makeRequest<CoachingPlan>('/api/mcp', {
      tool: 'create_practice_plan',
      parameters: {
        age_group: ageGroup,
        duration_minutes: durationMinutes,
        skills,
        number_of_players: options.number_of_players || 15,
        practice_context: options.practice_context || ''
      }
    })
  }

  /**
   * Create a player development plan
   */
  async createPlayerDevelopmentPlan(
    playerName: string,
    position: string,
    currentLevel: string,
    targetSkills: string[],
    timelineWeeks: number
  ): Promise<PlayerDevelopmentPlan> {
    return this.makeRequest<PlayerDevelopmentPlan>('/api/mcp', {
      tool: 'create_player_development_plan',
      parameters: {
        player_name: playerName,
        position,
        current_level: currentLevel,
        target_skills: targetSkills,
        timeline_weeks: timelineWeeks
      }
    })
  }

  /**
   * Health check for the MCP server
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/health`)
      return await response.json()
    } catch (error) {
      console.error('Health check failed:', error)
      throw error
    }
  }
}

// Export singleton instance
export const apiClient = new APIClient()
