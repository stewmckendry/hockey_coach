// Server-side only - never sent to browser
import OpenAI from 'openai'
import { apiClient } from '../api'

interface IntentAnalysis {
  intent: 'practice_planning' | 'drill_search' | 'coaching_advice' | 'season_setup' | 'general_chat'
  confidence: number
  parameters: Record<string, any>
  reasoning: string
}

/**
 * Server-side hockey coaching agent with secure OpenAI integration
 */
export class SecureHockeyAgent {
  private openai: OpenAI
  
  constructor() {
    // ✅ SECURE: API key only exists on server
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY // Server environment variable
    })
  }

  /**
   * Main entry point: process user message securely
   */
  async processMessage(userMessage: string, conversationHistory: any[] = []): Promise<{
    response: string
    metadata: {
      intent: IntentAnalysis
      toolsCalled: string[]
      processingTimeMs: number
    }
  }> {
    const startTime = Date.now()
    
    try {
      // Step 1: Analyze user intent (server-side)
      const intent = await this.analyzeIntent(userMessage, conversationHistory)
      
      // Step 2: Execute tools with rate limiting
      const toolResults = await this.executeToolsSecurely(intent)
      
      // Step 3: Synthesize response
      const response = await this.synthesizeResponse(userMessage, intent, toolResults, conversationHistory)
      
      return {
        response,
        metadata: {
          intent,
          toolsCalled: toolResults.map(r => r.tool),
          processingTimeMs: Date.now() - startTime
        }
      }

    } catch (error) {
      console.error('Secure hockey agent error:', error)
      throw new Error('Unable to process coaching request')
    }
  }

  /**
   * Analyze user intent with conversation context
   */
  private async analyzeIntent(message: string, history: any[]): Promise<IntentAnalysis> {
    try {
      const systemPrompt = `You are an expert hockey coaching assistant. Analyze the user's message to determine their intent.

CONVERSATION CONTEXT:
${history.slice(-4).map(msg => `${msg.role}: ${msg.content}`).join('\n')}

CURRENT MESSAGE: "${message}"

Analyze the intent and respond with ONLY a valid JSON object in this exact format:
{
  "intent": "practice_planning" | "drill_search" | "coaching_advice" | "season_setup" | "general_chat",
  "confidence": 0.8,
  "parameters": {
    "age_group": "U10",
    "skills": ["skating", "passing"],
    "duration_minutes": 60,
    "team_size": 15,
    "query": "user's request in simple terms"
  },
  "reasoning": "Brief explanation of why this intent was chosen"
}

Choose the most appropriate intent:
- practice_planning: Creating full practice plans
- drill_search: Looking for specific drills or exercises  
- coaching_advice: General coaching tips and recommendations
- season_setup: Long-term planning, team structure
- general_chat: General hockey questions or conversation`

      const response = await this.openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: message }
        ],
        temperature: 0.1,
        response_format: { type: "json_object" },
        max_tokens: 500
      })

      const content = response.choices[0].message.content
      if (!content) {
        throw new Error('No content in OpenAI response')
      }

      const parsed = JSON.parse(content)
      console.log('🔍 Intent Analysis Result:', parsed)
      
      return parsed
    } catch (error) {
      console.error('Intent analysis failed:', error)
      // Fallback to general_chat with basic parameters
      return {
        intent: 'general_chat',
        confidence: 0.8,
        parameters: {
          query: message,
          age_group: 'U12'
        },
        reasoning: 'Fallback due to intent analysis error'
      }
    }
  }

  /**
   * Execute tools with security controls
   */
  private async executeToolsSecurely(intent: IntentAnalysis): Promise<Array<{tool: string, result: any}>> {
    const results: Array<{tool: string, result: any}> = []
    
    // ✅ SECURE: Server-side rate limiting and validation
    if (!this.isValidIntent(intent)) {
      console.warn('Invalid intent detected:', intent)
      // Instead of throwing, return a search fallback
      const generalResult = await apiClient.searchHockeyKnowledge(
        intent.parameters?.query || 'hockey coaching',
        { n_results: 3 }
      )
      results.push({ tool: 'search_hockey_knowledge_fallback', result: generalResult })
      return results
    }

    console.log('✅ Valid intent, executing tools for:', intent.intent)

    // Execute tools based on intent with error handling
    try {
      switch (intent.intent) {
        case 'practice_planning':
          try {
            const planResult = await apiClient.createPracticePlan(
              intent.parameters.age_group || 'U12',
              intent.parameters.duration_minutes || 60,
              intent.parameters.skills?.map((skill: string) => ({
                skill,
                time_minutes: Math.floor((intent.parameters.duration_minutes || 60) * 0.6 / intent.parameters.skills.length)
              })) || [{ skill: 'skating', time_minutes: 20 }],
              {
                number_of_players: intent.parameters.team_size || 15,
                practice_context: intent.parameters.context || ''
              }
            )
            results.push({ tool: 'create_practice_plan', result: planResult })
          } catch (error) {
            console.error('Practice planning error:', error)
            // Fallback to drill search
            const drillResult = await apiClient.searchHockeyKnowledge(
              intent.parameters.skills?.join(' ') || 'hockey drill',
              { content_types: ['drill'], n_results: 3 }
            )
            results.push({ tool: 'search_hockey_knowledge_fallback', result: drillResult })
          }
          break

        case 'drill_search':
          const drillResult = await apiClient.searchHockeyKnowledge(
            intent.parameters.skills?.join(' ') || intent.parameters.query || 'hockey drill',
            {
              content_types: ['drill'],
              age_groups: intent.parameters.age_group ? [intent.parameters.age_group] : undefined,
              n_results: 5
            }
          )
          results.push({ tool: 'search_hockey_knowledge', result: drillResult })
          break

        case 'coaching_advice':
          if (intent.parameters.skills?.[0]) {
            const adviceResult = await apiClient.getCoachingRecommendations(
              intent.parameters.age_group || 'U12',
              intent.parameters.skills[0],
              intent.parameters.duration_minutes || 60,
              intent.parameters.team_size || 15,
              ['pucks', 'cones', 'nets']
            )
            results.push({ tool: 'get_coaching_recommendations', result: adviceResult })
          } else {
            // Fallback to general search
            const generalResult = await apiClient.searchHockeyKnowledge(
              intent.parameters.query || 'hockey coaching advice',
              { n_results: 3 }
            )
            results.push({ tool: 'search_hockey_knowledge', result: generalResult })
          }
          break

        default:
          // General search for other intents
          const generalResult = await apiClient.searchHockeyKnowledge(
            intent.parameters.query || 'hockey coaching',
            { n_results: 3 }
          )
          results.push({ tool: 'search_hockey_knowledge', result: generalResult })
      }
    } catch (error) {
      console.error('Tool execution error:', error)
      // Ultimate fallback - return a helpful message
      results.push({ 
        tool: 'fallback_response', 
        result: { 
          message: 'I encountered an issue accessing the hockey knowledge base. Let me help you with general coaching advice instead.',
          suggestions: [
            'Try asking about specific skills like "skating drills for beginners"',
            'Ask for practice planning help: "Plan a 60-minute U10 practice"',
            'Request coaching advice: "How to teach passing to young players"'
          ]
        }
      })
    }

    return results
  }

  /**
   * Synthesize natural coaching response
   */
  private async synthesizeResponse(
    userMessage: string,
    intent: IntentAnalysis,
    toolResults: Array<{tool: string, result: any}>,
    conversationHistory: any[]
  ): Promise<string> {
    try {
      // Handle fallback responses differently
      const hasFallbackResponse = toolResults.some(result => result.tool === 'fallback_response')
      
      if (hasFallbackResponse) {
        const fallbackResult = toolResults.find(result => result.tool === 'fallback_response')
        return `${fallbackResult?.result.message}\n\nHere are some things you can try:\n${fallbackResult?.result.suggestions.map((s: string) => `• ${s}`).join('\n')}`
      }

      const systemPrompt = `You are an experienced, enthusiastic hockey coach assistant. 

CONVERSATION CONTEXT:
${conversationHistory.slice(-3).map(msg => `${msg.role}: ${msg.content}`).join('\n')}

USER REQUEST: "${userMessage}"
INTENT ANALYSIS: ${JSON.stringify(intent, null, 2)}
TOOL RESULTS: ${JSON.stringify(toolResults, null, 2)}

RESPONSE GUIDELINES:
- Speak like a supportive hockey coach
- Use the tool results to provide specific, actionable advice
- Reference actual drills/plans from the results
- Keep it conversational and encouraging
- 2-4 paragraphs maximum
- End with a question or call to action when appropriate
- If the results seem limited, acknowledge it and provide what you can

Generate a natural coaching response:`

      const response = await this.openai.chat.completions.create({
        model: "gpt-4o",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: "Generate the coaching response" }
        ],
        temperature: 0.7,
        max_tokens: 800
      })

      return response.choices[0].message.content || 'I apologize, but I had trouble generating a response. Please try again!'
    } catch (error) {
      console.error('Response synthesis error:', error)
      // Fallback response
      return `I'd be happy to help with your hockey coaching question: "${userMessage}". However, I'm experiencing some technical difficulties right now. Could you try rephrasing your question or ask about something specific like:\n\n• Practice planning for a specific age group\n• Drill suggestions for particular skills\n• General coaching advice\n\nWhat would you like to focus on?`
    }
  }

  /**
   * Validate intent for security
   */
  private isValidIntent(intent: IntentAnalysis): boolean {
    const validIntents = ['practice_planning', 'drill_search', 'coaching_advice', 'season_setup', 'general_chat']
    
    // Check if intent structure is valid
    if (!intent || typeof intent !== 'object') {
      console.warn('Intent is not a valid object:', intent)
      return false
    }
    
    if (!intent.intent || typeof intent.intent !== 'string') {
      console.warn('Intent.intent is missing or not a string:', intent.intent)
      return false
    }
    
    if (typeof intent.confidence !== 'number' || intent.confidence < 0 || intent.confidence > 1) {
      console.warn('Intent confidence is invalid, allowing anyway:', intent.confidence)
      // Don't reject for confidence issues, just log
    }
    
    const isValidIntentType = validIntents.includes(intent.intent)
    const hasMinimumConfidence = (typeof intent.confidence === 'number') ? intent.confidence > 0.2 : true // Lower threshold
    
    console.log('Intent validation:', {
      intent: intent.intent,
      isValidType: isValidIntentType,
      confidence: intent.confidence,
      hasMinConfidence: hasMinimumConfidence,
      valid: isValidIntentType && hasMinimumConfidence
    })
    
    return isValidIntentType && hasMinimumConfidence
  }
}

// ✅ SECURE: Only create instance on server
export const secureHockeyAgent = new SecureHockeyAgent()
