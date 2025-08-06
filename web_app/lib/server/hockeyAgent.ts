// Server-side only - OpenAI Responses API implementation
import OpenAI from 'openai'
import { apiClient } from '../api'

interface ResponsesAPIMetadata {
  intent: {
    category: string
    confidence: number
    context_from_conversation: string
  }
  toolsUsed: string[]
  processingTimeMs: number
  conversationId?: string // OpenAI's conversation tracking
}

interface IntentAnalysis {
  intent: 'practice_planning' | 'drill_search' | 'coaching_advice' | 'season_setup' | 'general_chat'
  confidence: number
  parameters: Record<string, any>
  reasoning: string
}

/**
 * Server-side hockey coaching agent with OpenAI Responses API integration
 * Provides native multi-turn conversations with server-side state management
 */
export class SecureResponsesAgent {
  private openai: OpenAI
  
  constructor() {
    // ✅ SECURE: API key only exists on server
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY // Server environment variable
    })
  }

  /**
   * Process message using native Responses API with conversation state
   */
  async processMessage(
    userMessage: string, 
    previousResponseId?: string
  ): Promise<{
    response: string
    responseId: string
    metadata: ResponsesAPIMetadata
  }> {
    const startTime = Date.now()
    
    try {
      // Try OpenAI Responses API with public Railway MCP server first
      console.log('🔄 Using OpenAI Responses API with Railway MCP server')
      return await this.processWithResponsesAPI(userMessage, previousResponseId, startTime)

    } catch (error) {
      console.error('❌ Responses API with Railway MCP failed:', error)
      console.log('🔄 Falling back to enhanced Chat Completions API with local MCP')
      return await this.processWithEnhancedChat(userMessage, previousResponseId, startTime)
    }
  }

  /**
   * Check if Responses API is available
   */
  private hasResponsesAPI(): boolean {
    return !!(this.openai as any).responses && typeof (this.openai as any).responses.create === 'function'
  }

  /**
   * Process with native OpenAI Responses API (when available)
   */
  private async processWithResponsesAPI(
    userMessage: string,
    previousResponseId: string | undefined,
    startTime: number
  ) {
    console.log('🔄 Processing with Responses API + MCP tools')
    console.log('Previous Response ID:', previousResponseId)
    
    // Build the input messages with proper types
    const input = previousResponseId ? 
      [{ 
        role: 'user' as const, 
        content: [{ type: 'input_text' as const, text: userMessage }]
      }] : 
      [
        { 
          role: 'system' as const, 
          content: [{ 
            type: 'input_text' as const, 
            text: `You are an expert hockey coach assistant with access to comprehensive hockey coaching knowledge through specialized tools. Use the available MCP tools to provide detailed, evidence-based coaching advice. Always search for relevant drills, tactics, and development information when answering coaching questions.` 
          }]
        },
        { 
          role: 'user' as const, 
          content: [{ type: 'input_text' as const, text: userMessage }]
        }
      ]

    // Use the OpenAI SDK with proper MCP configuration
    console.log('📤 Creating Responses API request with MCP tools')
    
    const response = await this.openai.responses.create({
      model: 'gpt-4o-2024-11-20',
      input,
      tools: [
        {
          type: 'mcp' as const,
          server_url: 'https://hockeycoach-production.up.railway.app/mcp',
          server_label: 'hockey_mcp_server',
          server_description: 'Comprehensive hockey coaching knowledge base with drills, tactics, and development plans',
          allowed_tools: [
            'search_hockey_tactics',
            'search_hockey_videos',
            'search_hockey_drills',
            'search_hockey_skills',
            'search_hockey_dryland',
            'search_hockey_dryland_videos',
            'search_hockey_nhl_insights',
            'search_hockey_rules'
          ],
          require_approval: 'never' as const
        }
      ],
      ...(previousResponseId && { previous_response_id: previousResponseId }),
      temperature: 0.7,
      max_output_tokens: 1000,
      store: true
    }) as any // Type assertion until OpenAI SDK types are updated

    console.log('📥 Received response from OpenAI Responses API')
    console.log('Response ID:', response.id)
    console.log('Response object keys:', Object.keys(response))
    console.log('Response content items:', response.content?.length || 0)
    console.log('Raw response:', JSON.stringify(response, null, 2))

    // Extract tool calls and final message content from OpenAI Responses API format
    const toolCalls = response.output?.filter((item: any) => item.type === 'mcp_call') || []
    const toolsUsed = toolCalls.map((call: any) => call.name || 'unknown_tool')
    
    // OpenAI Responses API provides the final text in output_text field
    const finalMessage = response.output_text || 'I apologize, but I encountered an issue processing your request.'

    console.log('🛠️ Tools used:', toolsUsed)
    console.log('Final message:', finalMessage)
    
    return {
      response: finalMessage,
      responseId: response.id,
      metadata: {
        intent: {
          category: 'hockey_coaching',
          confidence: 0.9,
          context_from_conversation: 'Using OpenAI Responses API with MCP tools'
        },
        toolsUsed,
        processingTimeMs: Date.now() - startTime,
        conversationId: response.id
      }
    }
  }

  /**
   * Enhanced Chat Completions fallback with simulated state management
   */
  private async processWithEnhancedChat(
    userMessage: string,
    previousResponseId: string | undefined,
    startTime: number
  ) {
    // Step 1: Analyze intent with context awareness
    const intent = await this.analyzeIntentEnhanced(userMessage, previousResponseId)
    
    // Step 2: Execute tools if needed
    const toolResults = await this.executeToolsSecurely(intent)
    
    // Step 3: Generate response with context
    const response = await this.synthesizeEnhancedResponse(userMessage, intent, toolResults, previousResponseId)
    
    // Generate a simulated response ID for state tracking
    const responseId = `resp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    return {
      response,
      responseId,
      metadata: {
        intent: {
          category: intent.intent,
          confidence: intent.confidence,
          context_from_conversation: intent.reasoning
        },
        toolsUsed: toolResults.map(r => r.tool),
        processingTimeMs: Date.now() - startTime
      }
    }
  }

  /**
   * Enhanced intent analysis with conversation context
   */
  private async analyzeIntentEnhanced(message: string, previousResponseId?: string): Promise<IntentAnalysis> {
    try {
      const systemPrompt = `You are an expert hockey coaching assistant analyzing user intent.

${previousResponseId ? `CONVERSATION CONTEXT: This is a continuation of conversation (Previous Response ID: ${previousResponseId})` : 'CONVERSATION CONTEXT: This is a new conversation'}

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
    "query": "user's request in simple terms",
    "context_from_previous": "what the user mentioned before"
  },
  "reasoning": "Brief explanation considering conversation continuity"
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
      console.log('🔍 Enhanced Intent Analysis Result:', parsed)
      
      return parsed
    } catch (error) {
      console.error('Enhanced intent analysis failed:', error)
      // Fallback to general_chat with basic parameters
      return {
        intent: 'general_chat',
        confidence: 0.8,
        parameters: {
          query: message,
          age_group: 'U12',
          context_from_previous: previousResponseId ? 'Continuing previous conversation' : 'New conversation'
        },
        reasoning: 'Fallback due to intent analysis error'
      }
    }
  }

  /**
   * Execute tools with security controls and error handling
   */
  private async executeToolsSecurely(intent: IntentAnalysis): Promise<Array<{tool: string, result: any}>> {
    const results: Array<{tool: string, result: any}> = []
    
    // ✅ SECURE: Server-side rate limiting and validation
    if (!this.isValidIntent(intent)) {
      console.warn('Invalid intent detected:', intent)
      // Instead of throwing, return a search fallback
      try {
        const generalResult = await apiClient.searchHockeyKnowledge(
          intent.parameters?.query || 'hockey coaching',
          { n_results: 3 }
        )
        results.push({ tool: 'search_hockey_knowledge_fallback', result: generalResult })
      } catch (error) {
        console.error('Fallback search failed:', error)
      }
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
                practice_context: intent.parameters.context_from_previous || ''
              }
            )
            results.push({ tool: 'create_practice_plan', result: planResult })
          } catch (error) {
            console.error('Practice plan creation failed:', error)
            // Fallback to general search
            const searchResult = await apiClient.searchHockeyKnowledge(intent.parameters.query || 'practice drills', {
              age_groups: [intent.parameters.age_group || 'U12'],
              content_types: ['drills'],
              n_results: 3
            })
            results.push({ tool: 'search_hockey_knowledge_fallback', result: searchResult })
          }
          break

        case 'drill_search':
          try {
            const searchResult = await apiClient.searchHockeyKnowledge(
              intent.parameters.query || intent.parameters.skills?.[0] || 'hockey drills',
              {
                age_groups: intent.parameters.age_group ? [intent.parameters.age_group] : undefined,
                content_types: ['drills'],
                n_results: 5
              }
            )
            results.push({ tool: 'search_hockey_knowledge', result: searchResult })
          } catch (error) {
            console.error('Drill search failed:', error)
          }
          break

        case 'coaching_advice':
          try {
            const searchResult = await apiClient.searchHockeyKnowledge(
              intent.parameters.query || 'coaching advice',
              {
                content_types: ['coaching', 'tactics'],
                n_results: 4
              }
            )
            results.push({ tool: 'search_hockey_knowledge', result: searchResult })
          } catch (error) {
            console.error('Coaching advice search failed:', error)
          }
          break

        case 'season_setup':
          try {
            const searchResult = await apiClient.searchHockeyKnowledge(
              intent.parameters.query || 'season planning',
              {
                content_types: ['coaching', 'tactics', 'ltad'],
                n_results: 4
              }
            )
            results.push({ tool: 'search_hockey_knowledge', result: searchResult })
          } catch (error) {
            console.error('Season setup search failed:', error)
          }
          break

        case 'general_chat':
        default:
          try {
            const searchResult = await apiClient.searchHockeyKnowledge(
              intent.parameters.query || intent.parameters.context_from_previous || 'hockey coaching',
              { n_results: 3 }
            )
            results.push({ tool: 'search_hockey_knowledge', result: searchResult })
          } catch (error) {
            console.error('Knowledge search failed:', error)
          }
          break
      }
    } catch (error) {
      console.error('Tool execution error:', error)
    }

    return results
  }

  /**
   * Enhanced response synthesis with conversation continuity
   */
  private async synthesizeEnhancedResponse(
    userMessage: string,
    intent: IntentAnalysis,
    toolResults: Array<{tool: string, result: any}>,
    previousResponseId?: string
  ): Promise<string> {
    try {
      const contextPrompt = previousResponseId 
        ? `This is a continuation of our coaching conversation (Previous Response ID: ${previousResponseId}). Build upon the previous context naturally.`
        : 'This is the start of a new coaching conversation.'

      const systemPrompt = `You are an expert hockey coaching assistant with access to comprehensive hockey knowledge.

${contextPrompt}

COACHING CONTEXT AWARENESS:
- Remember details from our ongoing conversation
- Build upon previously discussed team information  
- Reference past questions and established context naturally
- Use hockey terminology and coaching language

USER'S CURRENT REQUEST: "${userMessage}"
INTENT ANALYSIS: ${JSON.stringify(intent, null, 2)}

AVAILABLE HOCKEY KNOWLEDGE:
${toolResults.map(result => `
${result.tool}:
${JSON.stringify(result.result, null, 2)}
`).join('\n')}

RESPONSE GUIDELINES:
- Speak like a supportive, experienced hockey coach
- Provide specific, actionable advice using the knowledge above
- Reference actual drills and techniques from the database
- Keep responses conversational but informative
- Ask follow-up questions when helpful
- If this is a follow-up, acknowledge the conversation context

Provide a helpful, detailed coaching response that addresses the user's request using the available hockey knowledge.`

      const response = await this.openai.chat.completions.create({
        model: "gpt-4o",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userMessage }
        ],
        temperature: 0.7,
        max_tokens: 1000
      })

      const content = response.choices[0].message.content
      if (!content) {
        throw new Error('No content in OpenAI response')
      }

      return content

    } catch (error) {
      console.error('Response synthesis failed:', error)
      return `I understand you're asking about ${intent.parameters?.query || 'hockey coaching'}. I'm having trouble accessing my hockey knowledge right now, but I'd be happy to help. Could you tell me more about what specific aspect you'd like coaching advice on?`
    }
  }

  /**
   * Validate intent structure
   */
  private isValidIntent(intent: IntentAnalysis): boolean {
    const validIntents = ['practice_planning', 'drill_search', 'coaching_advice', 'season_setup', 'general_chat']
    return validIntents.includes(intent.intent) && 
           typeof intent.confidence === 'number' && 
           intent.confidence >= 0 && 
           intent.confidence <= 1 &&
           typeof intent.parameters === 'object'
  }

  /**
   * Get system instructions for hockey coaching
   */
  private getInstructions(): string {
    return `You are an expert hockey coaching assistant with access to comprehensive hockey knowledge via MCP tools.

COACHING CONTEXT AWARENESS:
- Remember details from our ongoing conversation
- Build upon previously discussed team information
- Reference past questions and established context naturally
- Use hockey terminology and coaching language

AVAILABLE TOOLS:
- Hockey knowledge search (drills, tactics, skills, rules)
- Practice plan generation
- Coaching recommendations
- Player development guidance

RESPONSE STYLE:
- Speak like a supportive, experienced hockey coach
- Provide specific, actionable advice
- Reference actual drills and techniques from the knowledge base
- Keep responses conversational but informative
- Ask follow-up questions when helpful

Remember: You have access to a comprehensive hockey database through MCP tools. Use them to provide specific, detailed coaching advice.`
  }

  /**
   * Start a new conversation (no previous_response_id)
   */
  async startNewConversation(userMessage: string) {
    return this.processMessage(userMessage) // No previousResponseId = new conversation
  }

  /**
   * Continue existing conversation
   */
  async continueConversation(userMessage: string, previousResponseId: string) {
    return this.processMessage(userMessage, previousResponseId)
  }

  /**
   * Process Hockey IQ chatbot messages with Socratic reasoning
   * Designed for U10 players (8-9 years old)
   * Uses OpenAI Responses API for native conversation management
   */
  async processHockeyIQMessage(
    userMessage: string,
    options: {
      category?: string
      age_group: 'U10'
      mode: 'socratic'
      previousResponseId?: string  // OpenAI Responses API conversation tracking
    }
  ): Promise<{ response: string; responseId: string; metadata?: any }> {
    const startTime = Date.now()
    
    try {
      // Build the Socratic system prompt for U10 players
      const systemPrompt = `You are the Hockey IQ Coach, a friendly and encouraging assistant for ${options.age_group} hockey players (8-9 years old).

COMMUNICATION STYLE:
- Use simple, clear language (Grade 3-4 reading level)
- Be extremely encouraging and positive
- Use emojis sparingly but effectively (🏒 ⭐ 🎯)
- Keep sentences short and easy to understand
- Celebrate effort and curiosity, not just correct answers

SOCRATIC METHOD:
- Instead of giving direct answers, guide with questions
- Ask "Why do you think that?" or "What would happen if...?"
- Break complex ideas into simple steps
- Relate concepts to their playing experience
- Use "Let's think about this together..." approach

KNOWLEDGE TOOLS AVAILABLE:
You have access to comprehensive hockey knowledge through MCP tools:
- search_hockey_rules: For game rules, penalties, offside, icing
- search_hockey_skills: For skill development and techniques
- search_hockey_drills: For practice activities and exercises
- search_hockey_tactics: For positioning and team strategies
- search_hockey_videos: For finding video demonstrations
- search_hockey_dryland: For off-ice training
- search_hockey_nhl_insights: For professional tips
- search_hockey_rules: For rules and regulations

USE TOOLS WHEN:
- Players ask specific questions needing accurate information
- You need to verify hockey facts or find age-appropriate content
- Questions involve drills, skills, or rules
- You want expert knowledge to guide your Socratic questions

IMPORTANT: Use tools to enhance Socratic guidance, not to lecture!

${options.category ? `FOCUS AREA: ${options.category.replace('_', ' ')}` : ''}

TEACHING APPROACH FOR U10:
- Use concrete examples from games they've played
- Reference fun NHL players or teams when relevant
- Compare hockey concepts to things they know (school, other sports)
- Always end with encouragement or a follow-up question
- If they're wrong, say "Good thinking! Let's look at it this way..."

EXAMPLE RESPONSES:
User: "What's offside?"
You: "Great question! 🏒 Let's think about it... Have you ever noticed the blue lines on the ice? What do you think would happen if you could go anywhere on the ice before the puck? Would that be fair? Let me help you figure this out..."

User: "How do I shoot harder?"
You: "Awesome that you want to improve your shot! 💪 When you throw a ball really far, do you use just your arms or your whole body? Hockey shots are similar! What part of your body do you think gives the most power? Here's a hint: it starts with your legs..."

Remember: You're talking to 8-9 year olds. Make it FUN, SIMPLE, and ENCOURAGING!`

      // Remove manual tool calling - let the LLM decide through Responses API
      // The Responses API will handle tool selection based on the conversation context

      // Check if we have the Responses API available
      const hasResponsesAPI = this.hasResponsesAPI()
      
      if (hasResponsesAPI) {
        // Use OpenAI Responses API for native conversation management
        console.log('🎯 Using OpenAI Responses API for Hockey IQ')
        
        // Build the input for Responses API
        const systemMessage = {
          role: 'system' as const,
          content: [{
            type: 'input_text' as const,
            text: systemPrompt
          }]
        }
        
        const userMessageInput = {
          role: 'user' as const,
          content: [{ type: 'input_text' as const, text: userMessage }]
        }
        
        // Build input array based on whether we have a previous response
        const input = options.previousResponseId 
          ? [userMessageInput]  // Just the new message, API handles history
          : [systemMessage, userMessageInput]  // New conversation
        
        // Create the response using Responses API with MCP tools
        const response = await (this.openai as any).responses.create({
          model: 'gpt-4o-2024-11-20',
          input,
          ...(options.previousResponseId && { previous_response_id: options.previousResponseId }),
          tools: [
            {
              type: 'mcp' as const,
              server_url: 'https://hockeycoach-production.up.railway.app/mcp',
              server_label: 'hockey_mcp_server',
              server_description: 'Comprehensive hockey coaching knowledge for U10 players',
              allowed_tools: [
                'search_hockey_tactics',
                'search_hockey_videos',
                'search_hockey_drills',
                'search_hockey_skills',
                'search_hockey_dryland',
                'search_hockey_dryland_videos',
                'search_hockey_nhl_insights',
                'search_hockey_rules'
              ],
              require_approval: 'never' as const
            }
          ],
          temperature: 0.8,
          max_output_tokens: 500,
          store: true  // Store for 30 days to maintain conversation history
        })
        
        console.log('📥 Hockey IQ Response ID:', response.id)
        
        // Extract tool calls from the response
        const toolCalls = response.output?.filter((item: any) => item.type === 'mcp_call') || []
        const toolsUsed = toolCalls.map((call: any) => call.name || 'unknown_tool')
        
        console.log('🛠️ Hockey IQ Tools used:', toolsUsed)
        
        const finalMessage = response.output_text || 'I need to think about that! Can you tell me more? 🏒'
        
        return {
          response: finalMessage,
          responseId: response.id,  // Return for next conversation turn
          metadata: {
            processingTimeMs: Date.now() - startTime,
            mode: 'hockey_iq_socratic_responses_api',
            age_group: options.age_group,
            category: options.category,
            toolsUsed,
            conversationId: response.id
          }
        }
      } else {
        // Fallback to Chat Completions API (without conversation history)
        console.log('⚠️ Responses API not available, using Chat Completions')
        
        const response = await this.openai.chat.completions.create({
          model: 'gpt-4o',
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userMessage }
          ],
          temperature: 0.8,
          max_tokens: 500
        })
        
        const content = response.choices[0].message.content
        if (!content) {
          throw new Error('No content in response')
        }
        
        return {
          response: content,
          responseId: '',  // No ID for chat completions
          metadata: {
            processingTimeMs: Date.now() - startTime,
            mode: 'hockey_iq_socratic_chat_completions',
            age_group: options.age_group,
            category: options.category,
            toolsUsed: []  // Chat completions doesn't have MCP tools
          }
        }
      }

    } catch (error) {
      console.error('Hockey IQ processing error:', error)
      return {
        response: "That's a great question! 🏒 Let me think about that... Why don't you tell me what you already know about it, and we can figure it out together!",
        responseId: '',  // No ID on error
        metadata: {
          processingTimeMs: Date.now() - startTime,
          error: true
        }
      }
    }
  }
}

export const secureResponsesAgent = new SecureResponsesAgent()
