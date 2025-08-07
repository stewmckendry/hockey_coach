/**
 * Dynamic Quiz Generator
 * Generates quiz questions using MCP tools research and Thunder playbook context
 */

import OpenAI from 'openai'
import { quizCache } from './quizCache'
import thunderPlaybook from '@/data/thunder-playbook.json'

// Import existing static questions as fallback
import questionsData from '@/data/hockey-iq-questions.json'

// Define Question type locally to avoid circular dependencies
export interface Question {
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
  // Dynamic generation fields
  thunderContext?: string
  researchSource?: string
}

interface GenerationOptions {
  category: string
  difficulty?: 'rookie' | 'player' | 'allstar'
  includeThunderContext?: boolean
  useCache?: boolean
}

interface MCPSearchResult {
  content: string
  source: string
  relevance: number
}

class DynamicQuizGenerator {
  private openai: OpenAI
  private mcpBaseUrl: string
  
  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    })
    // Use local MCP server in development, Railway in production
    this.mcpBaseUrl = process.env.MCP_SERVER_URL || 
      (process.env.NODE_ENV === 'production' 
        ? 'https://hockey-mcp-production.up.railway.app'
        : 'http://localhost:3003/api')  // Local direct API wrapper
  }

  /**
   * Main entry point for quiz question generation
   */
  async generateQuestion(options: GenerationOptions): Promise<Question> {
    const { category, difficulty = 'rookie', includeThunderContext = true, useCache = true } = options

    // Check cache first
    if (useCache) {
      const cachedQuestion = quizCache.getQuestion(category)
      if (cachedQuestion) {
        console.log(`[Quiz] Returning cached question for ${category}`)
        return cachedQuestion
      }
    }

    try {
      // Generate new question with research
      console.log(`[Quiz] Generating new question for ${category}`)
      const question = await this.generateWithResearch(category, difficulty, includeThunderContext)
      
      // Add to cache
      quizCache.addQuestion(category, question, question.thunderContext, question.researchSource)
      
      return question
    } catch (error) {
      console.error('[Quiz] Generation failed, falling back to static:', error)
      return this.getStaticFallback(category)
    }
  }

  /**
   * Generate question with MCP research and Thunder context
   */
  private async generateWithResearch(
    category: string, 
    difficulty: string,
    includeThunderContext: boolean
  ): Promise<Question> {
    // Step 1: Research from MCP tools
    const research = await this.searchHockeyKnowledge(category)
    
    // Step 2: Get Thunder context if applicable
    const thunderContext = includeThunderContext ? this.getThunderContext(category) : null
    
    // Step 3: Generate question using LLM
    const prompt = this.buildGenerationPrompt(category, difficulty, research, thunderContext)
    
    const completion = await this.openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        { 
          role: 'system', 
          content: 'You are creating hockey quiz questions for U10 players (ages 8-9). Make questions fun, educational, and age-appropriate.'
        },
        { role: 'user', content: prompt }
      ],
      temperature: 0.7,
      response_format: { type: 'json_object' }
    })

    const generatedData = JSON.parse(completion.choices[0].message.content || '{}')
    
    // Format as Question interface
    const question: Question = {
      id: `dynamic_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      category: category as any,
      level: difficulty as any,
      question: generatedData.question,
      correctAnswer: generatedData.correctAnswer,
      hints: generatedData.hints || ["Think about what you learned!", "Remember the basics!"],
      followUpQuestions: generatedData.followUpQuestions || ["Why do you think that's important?"],
      encouragementMessages: {
        correct: generatedData.correctMessage || "Great job! You're a hockey star! 🌟",
        incorrect: generatedData.incorrectMessage || "Good try! Let's learn together!"
      },
      funFact: generatedData.funFact,
      thunderContext: thunderContext?.description,
      researchSource: research.source
    }

    return question
  }

  /**
   * Search hockey knowledge using MCP tools
   */
  private async searchHockeyKnowledge(category: string): Promise<MCPSearchResult> {
    try {
      // Special handling for fun_facts - use Exa web search
      if (category === 'fun_facts') {
        return await this.searchWithExa(category)
      }

      // Map category to appropriate MCP tool - using ACTUAL tools from hockey_mcp.py
      const toolMapping: Record<string, string> = {
        'rules': 'search_hockey_rules',        // Searches rule collections
        'positioning': 'search_hockey_tactics', // Searches tactics collection
        'skills': 'search_hockey_skills',      // Searches skills collection
        'teamwork': 'search_hockey_tactics',   // Teamwork is part of tactics
      }

      const tool = toolMapping[category] || 'search_hockey_skills' // Default to skills
      
      // Call MCP server via HTTP - use correct endpoint path
      const endpoint = this.mcpBaseUrl.includes('localhost') 
        ? `${this.mcpBaseUrl}/mcp`  // Local endpoint: http://localhost:3003/api/mcp
        : `${this.mcpBaseUrl}/mcp/execute`  // Railway endpoint
        
      const requestBody = {
        tool: tool,  // Use the mapped tool, not a hardcoded one
        parameters: {  // Direct API expects 'parameters' not 'args'
          query: this.getCategorySearchQuery(category)
        }
      }
      
      console.log('[Quiz] MCP Request:', { endpoint, tool, body: requestBody })
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'  // Add Accept header to prevent 406 errors
        },
        body: JSON.stringify(requestBody)
      })
      
      console.log('[Quiz] MCP Response:', response.status, response.statusText)

      if (!response.ok) {
        throw new Error(`MCP search failed: ${response.statusText}`)
      }

      const data = await response.json()
      
      // Direct API returns { success: true, data: { content: [...] } }
      // Each content item has text field with JSON string containing the hockey knowledge
      if (data && data.success && data.data && data.data.content && Array.isArray(data.data.content)) {
        // Combine the top results into research content
        const topResults = data.data.content.slice(0, 3) // Use top 3 results
        const combinedContent = topResults.map((item: any) => {
          // Parse the JSON string from the text field
          const result = JSON.parse(item.text)
          const parts = []
          if (result.title) parts.push(result.title)
          if (result.summary) parts.push(result.summary)
          if (result.teaching_points) parts.push(`Teaching points: ${result.teaching_points}`)
          if (result.skills_practiced) parts.push(`Skills: ${result.skills_practiced}`)
          return parts.join('. ')
        }).join('\n\n')
        
        return {
          content: combinedContent || this.getDefaultKnowledge(category),
          source: tool,
          relevance: 0.9
        }
      }
      
      // Fallback if no results
      return {
        content: this.getDefaultKnowledge(category),
        source: tool,
        relevance: 0.5
      }
    } catch (error) {
      console.error('[Quiz] MCP search failed:', error)
      // Return default knowledge as fallback
      return {
        content: this.getDefaultKnowledge(category),
        source: 'default',
        relevance: 0.3
      }
    }
  }

  /**
   * Search using Exa web search for fun facts
   */
  private async searchWithExa(category: string): Promise<MCPSearchResult> {
    try {
      // Check if Exa API key is configured
      const exaApiKey = process.env.EXA_API_KEY
      
      if (!exaApiKey) {
        console.log('[Quiz] Exa API key not configured, falling back to NHL insights')
        return await this.searchHockeyKnowledgeFallback('fun_facts')
      }
      
      const query = this.getCategorySearchQuery(category)
      
      console.log('[Quiz] Exa API Request:', { query, numResults: 5 })
      
      // Call Exa API directly (server-side only, API key is safe)
      const response = await fetch('https://api.exa.ai/search', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${exaApiKey}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          query: query,
          numResults: 5,
          useAutoprompt: true,  // Improves search quality
          type: 'neural',       // Use neural search for better results
          contents: {
            text: true          // Include text content in results
          },
          highlights: {
            numSentences: 3,    // Get 3 sentence highlights
            highlightsPerUrl: 1 // One highlight per URL
          }
        })
      })
      
      console.log('[Quiz] Exa API Response:', response.status, response.statusText)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('[Quiz] Exa API error:', errorText)
        throw new Error(`Exa API failed: ${response.statusText}`)
      }

      const data = await response.json()
      
      // Parse Exa API response
      if (data && data.results && Array.isArray(data.results)) {
        // Combine the top results into research content
        const topResults = data.results.slice(0, 3)
        const combinedContent = topResults.map((result: any) => {
          const parts = []
          
          // Use the title and highlight/text for context
          if (result.title) parts.push(result.title)
          
          // Prefer highlights over full text (more concise)
          if (result.highlights && result.highlights.length > 0) {
            parts.push(result.highlights.join(' '))
          } else if (result.text) {
            // Truncate text if too long
            const text = result.text.substring(0, 500)
            parts.push(text)
          } else if (result.snippet) {
            parts.push(result.snippet)
          }
          
          // Add URL for reference (though we won't show it to kids)
          if (result.url) {
            console.log(`[Quiz] Exa source: ${result.url}`)
          }
          
          return parts.join('. ')
        }).join('\n\n')
        
        console.log(`[Quiz] Exa returned ${data.results.length} results, using top 3`)
        
        return {
          content: combinedContent || this.getDefaultKnowledge(category),
          source: 'exa_web_search',
          relevance: 0.95  // Exa provides highly relevant current content
        }
      }
      
      // Fallback if unexpected response format
      console.log('[Quiz] Exa API returned unexpected format, falling back')
      return {
        content: this.getDefaultKnowledge(category),
        source: 'exa_web_search',
        relevance: 0.5
      }
    } catch (error) {
      console.error('[Quiz] Exa API call failed, falling back to NHL insights:', error)
      console.error('[Quiz] Exa API error details:', error instanceof Error ? error.message : error)
      // Fall back to NHL insights tool when Exa fails
      return await this.searchHockeyKnowledgeFallback('fun_facts')
    }
  }

  /**
   * Fallback search using local hockey MCP tools
   */
  private async searchHockeyKnowledgeFallback(category: string): Promise<MCPSearchResult> {
    try {
      const tool = 'search_hockey_nhl_insights' // Use NHL insights for fun facts
      
      const endpoint = this.mcpBaseUrl.includes('localhost') 
        ? `${this.mcpBaseUrl}/mcp`
        : `${this.mcpBaseUrl}/mcp/execute`
        
      const requestBody = {
        tool: tool,
        parameters: {
          query: 'hockey history NHL players Stanley Cup records'
        }
      }
      
      console.log('[Quiz] Fallback MCP Request:', { endpoint, tool })
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(requestBody)
      })
      
      if (!response.ok) {
        throw new Error(`Fallback search failed: ${response.statusText}`)
      }

      const data = await response.json()
      
      if (data && data.success && data.data && data.data.content && Array.isArray(data.data.content)) {
        const topResults = data.data.content.slice(0, 3)
        const combinedContent = topResults.map((item: any) => {
          const result = JSON.parse(item.text)
          const parts = []
          if (result.title) parts.push(result.title)
          if (result.summary) parts.push(result.summary)
          if (result.teaching_points) parts.push(`Teaching points: ${result.teaching_points}`)
          return parts.join('. ')
        }).join('\n\n')
        
        return {
          content: combinedContent || this.getDefaultKnowledge(category),
          source: 'search_hockey_nhl_insights',
          relevance: 0.9
        }
      }
      
      return {
        content: this.getDefaultKnowledge(category),
        source: 'search_hockey_nhl_insights',
        relevance: 0.5
      }
    } catch (error) {
      console.error('[Quiz] Fallback search also failed:', error)
      return {
        content: this.getDefaultKnowledge(category),
        source: 'default',
        relevance: 0.3
      }
    }
  }

  /**
   * Get Thunder-specific context for the category
   */
  private getThunderContext(category: string): any {
    const contextMap: Record<string, any> = {
      'rules': null, // Rules are universal, no Thunder context
      'positioning': thunderPlaybook.systems.breakouts.upAndWheel,
      'skills': {
        description: `Thunder emphasizes: ${thunderPlaybook.teamIdentity.values.join(', ')}`,
        keyPoints: thunderPlaybook.teamIdentity.values
      },
      'teamwork': {
        description: thunderPlaybook.teamIdentity.motto,
        style: thunderPlaybook.teamIdentity.style
      },
      'fun_facts': {
        description: `Thunder Hockey: ${thunderPlaybook.teamIdentity.motto}`,
        values: thunderPlaybook.teamIdentity.values
      }
    }

    return contextMap[category] || null
  }

  /**
   * Build LLM prompt for question generation
   */
  private buildGenerationPrompt(
    category: string,
    difficulty: string,
    research: MCPSearchResult,
    thunderContext: any
  ): string {
    let prompt = `Generate a hockey quiz question for U10 players (ages 8-9).

Category: ${category}
Difficulty: ${difficulty}
Research Content: ${research.content}

Requirements:
- Question should test understanding, not memorization
- Language must be simple and encouraging
- Include 2 helpful hints that guide thinking
- Add a fun fact that kids will remember
- Make it engaging and fun!
`

    if (thunderContext) {
      prompt += `
Thunder Team Context:
${JSON.stringify(thunderContext, null, 2)}

Include Thunder-specific elements where relevant. For example:
- "In Thunder's system..." 
- "Like we practice at Thunder..."
- Reference Thunder values: ${thunderPlaybook.teamIdentity.values.join(', ')}
`
    }

    prompt += `
Return a JSON object with:
{
  "question": "The quiz question",
  "correctAnswer": "The correct answer", 
  "hints": ["Hint 1", "Hint 2"],
  "followUpQuestions": ["Follow-up 1", "Follow-up 2"],
  "correctMessage": "Encouragement when correct",
  "incorrectMessage": "Encouragement when incorrect",
  "funFact": "An interesting fact related to the question"
}
`

    return prompt
  }

  /**
   * Get search query for category
   */
  private getCategorySearchQuery(category: string): string {
    const queries: Record<string, string> = {
      'rules': 'hockey rules penalties offsides icing basics',
      'positioning': 'hockey positions defensive offensive zone coverage',
      'skills': 'hockey skating passing shooting stickhandling techniques',
      'teamwork': 'hockey teamwork communication support systems',
      'fun_facts': 'interesting hockey facts NHL records amazing hockey statistics fun hockey trivia for kids 2024'
    }
    
    return queries[category] || 'hockey basics for kids'
  }

  /**
   * Get default knowledge when MCP fails
   */
  private getDefaultKnowledge(category: string): string {
    const defaults: Record<string, string> = {
      'rules': 'Hockey has rules about offsides, icing, and penalties to keep the game fair and safe.',
      'positioning': 'Players have specific positions: center, wings, defense, and goalie, each with important roles.',
      'skills': 'Key hockey skills include skating, passing, shooting, and stickhandling.',
      'teamwork': 'Hockey is a team sport where communication and supporting teammates is crucial.',
      'fun_facts': 'Hockey is one of the fastest team sports, with players skating up to 25 mph!'
    }
    
    return defaults[category] || 'Hockey is an exciting sport that requires skill, teamwork, and strategy.'
  }

  /**
   * Get static question as fallback
   */
  private getStaticFallback(category: string): Question {
    const categoryQuestions = questionsData.questions.filter(q => q.category === category)
    const questions = categoryQuestions.length > 0 ? categoryQuestions : questionsData.questions
    
    const randomQuestion = questions[Math.floor(Math.random() * questions.length)]
    
    // Ensure all required fields are present
    return {
      ...randomQuestion,
      funFact: randomQuestion.funFact || 'Hockey is an amazing sport!',
      thunderContext: undefined,
      researchSource: 'static'
    } as Question
  }

  /**
   * Preload questions for common categories
   */
  async preloadQuestions(): Promise<void> {
    const categories = ['rules', 'positioning', 'skills', 'teamwork', 'fun_facts']
    
    console.log('[Quiz] Starting question preload...')
    
    await quizCache.preloadCategories(categories, async (category) => {
      return await this.generateQuestion({ 
        category, 
        useCache: false // Don't use cache when preloading
      })
    })
    
    console.log('[Quiz] Preload complete. Cache stats:', quizCache.getStats())
  }

  /**
   * Get cache statistics for monitoring
   */
  getCacheStats() {
    return quizCache.getStats()
  }
}

// Export singleton instance
export const dynamicQuizGenerator = new DynamicQuizGenerator()

// Export the dynamic quiz generator instance