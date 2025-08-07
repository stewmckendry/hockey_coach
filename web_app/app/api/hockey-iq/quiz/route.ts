import { NextRequest, NextResponse } from 'next/server'
import { secureResponsesAgent } from '@/lib/server/hockeyAgent'
import questionsData from '@/data/hockey-iq-questions.json'
import { dynamicQuizGenerator } from '@/lib/server/dynamicQuizGenerator'
import '@/lib/server/initializeQuizCache' // Trigger cache initialization
import OpenAI from 'openai'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Validate input
    if (!body.action || typeof body.action !== 'string') {
      return NextResponse.json(
        { error: 'Invalid action' },
        { status: 400 }
      )
    }

    switch (body.action) {
      case 'get_question': {
        // Use hybrid approach: Try dynamic generation first, fallback to static
        const category = body.category
        const useDynamic = body.useDynamic !== false // Default to true
        
        try {
          if (useDynamic) {
            // Try dynamic generation with caching
            console.log(`[Quiz API] Attempting dynamic generation for category: ${category}`)
            const dynamicQuestion = await dynamicQuizGenerator.generateQuestion({
              category: category || 'rules',
              difficulty: body.difficulty || 'rookie',
              includeThunderContext: body.includeThunderContext !== false,
              useCache: true
            })
            
            return NextResponse.json({
              success: true,
              question: dynamicQuestion,
              source: 'dynamic',
              timestamp: new Date().toISOString()
            })
          }
        } catch (error) {
          console.error('[Quiz API] Dynamic generation failed:', error)
          // Fall through to static questions
        }
        
        // Fallback to static questions
        console.log(`[Quiz API] Using static questions for category: ${category}`)
        const questions = category 
          ? questionsData.questions.filter(q => q.category === category)
          : questionsData.questions
        
        if (questions.length === 0) {
          return NextResponse.json(
            { error: 'No questions available' },
            { status: 404 }
          )
        }
        
        const randomQuestion = questions[Math.floor(Math.random() * questions.length)]
        
        return NextResponse.json({
          success: true,
          question: randomQuestion,
          source: 'static',
          timestamp: new Date().toISOString()
        })
      }

      case 'evaluate_answer': {
        // Evaluate user's answer using AI for flexible matching
        const { questionId, userAnswer, questionText, correctAnswer } = body
        
        if (!questionId || !userAnswer) {
          return NextResponse.json(
            { error: 'Missing question ID or answer' },
            { status: 400 }
          )
        }

        // Try to find question in static data first
        let question = questionsData.questions.find(q => q.id === questionId)
        
        // If not found and it's a dynamic question, use the provided question data
        if (!question && questionId.startsWith('dynamic_')) {
          if (!questionText || !correctAnswer) {
            return NextResponse.json(
              { error: 'Dynamic question data missing' },
              { status: 400 }
            )
          }
          // Create a temporary question object for evaluation
          question = {
            id: questionId,
            question: questionText,
            correctAnswer: correctAnswer,
            encouragementMessages: {
              correct: "Great job! You're a hockey star! 🌟",
              incorrect: "Good try! Let's learn together!"
            },
            funFact: body.funFact || "Hockey is an amazing sport!",
            followUpQuestions: body.followUpQuestions || ["Why do you think that's important?"]
          } as any
        }
        
        if (!question) {
          return NextResponse.json(
            { error: 'Question not found' },
            { status: 404 }
          )
        }

        // Use AI to evaluate if the answer is correct (allows for variations)
        const evaluationPrompt = `
You are evaluating a U10 hockey player's answer to a quiz question.

Question: ${question.question}
Correct Answer: ${question.correctAnswer}
User's Answer: ${userAnswer}

Determine if the user's answer is correct. Be lenient with spelling and phrasing for 8-9 year olds.
Accept answers that have the right idea even if not perfectly worded.

Respond with a JSON object:
{
  "correct": true/false,
  "feedback": "encouraging message",
  "explanation": "simple explanation if wrong"
}
`

        // Create a new OpenAI client for evaluation
        const openai = new OpenAI({
          apiKey: process.env.OPENAI_API_KEY
        })
        
        const evaluation = await openai.chat.completions.create({
          model: 'gpt-4o',
          messages: [
            { role: 'system', content: evaluationPrompt },
            { role: 'user', content: userAnswer }
          ],
          temperature: 0.3,
          response_format: { type: 'json_object' }
        })

        const result = JSON.parse(evaluation.choices[0].message.content || '{}')
        
        return NextResponse.json({
          success: true,
          correct: result.correct,
          feedback: result.feedback || question.encouragementMessages[result.correct ? 'correct' : 'incorrect'],
          explanation: result.explanation,
          correctAnswer: question.correctAnswer,
          funFact: result.correct ? question.funFact : undefined,
          followUpQuestion: result.correct ? question.followUpQuestions[0] : undefined,
          timestamp: new Date().toISOString()
        })
      }

      case 'get_hint': {
        // Get a hint for the current question
        const { questionId, hintIndex = 0, hints } = body
        
        // Try to find question in static data first
        let questionHints = questionsData.questions.find(q => q.id === questionId)?.hints
        
        // If not found and it's a dynamic question, use the provided hints
        if (!questionHints && questionId.startsWith('dynamic_')) {
          if (!hints || !Array.isArray(hints)) {
            return NextResponse.json(
              { error: 'Dynamic question hints missing' },
              { status: 400 }
            )
          }
          questionHints = hints
        }
        
        if (!questionHints) {
          return NextResponse.json(
            { error: 'Question not found' },
            { status: 404 }
          )
        }

        const hint = questionHints[Math.min(hintIndex, questionHints.length - 1)]
        
        return NextResponse.json({
          success: true,
          hint,
          hasMoreHints: hintIndex < questionHints.length - 1,
          timestamp: new Date().toISOString()
        })
      }

      case 'get_stats': {
        // Get quiz generation statistics
        const stats = {
          cacheStats: dynamicQuizGenerator.getCacheStats(),
          totalGenerated: 0,
          fromMCP: 0,
          fromStatic: 0,
          cacheHitRate: 0,
          cacheHits: 0,
          cacheMisses: 0,
          avgGenerationTime: 3000,
          categoryBreakdown: {},
          toolUsage: {}
        }
        
        // Calculate totals from cache stats
        if (stats.cacheStats) {
          Object.values(stats.cacheStats).forEach((category: any) => {
            stats.totalGenerated += category.total || 0
            stats.fromMCP += category.valid || 0
            stats.cacheHits += category.valid || 0
            stats.cacheMisses += category.expired || 0
          })
          
          // Estimate static vs MCP (if cache has items, they're likely from MCP)
          stats.fromStatic = Math.max(0, stats.totalGenerated - stats.fromMCP)
          
          // Calculate cache hit rate
          const totalRequests = stats.cacheHits + stats.cacheMisses
          stats.cacheHitRate = totalRequests > 0 ? 
            Math.round((stats.cacheHits / totalRequests) * 100) : 0
        }
        
        return NextResponse.json(stats)
      }

      case 'preload_questions': {
        // Preload questions for all categories to warm the cache
        try {
          await dynamicQuizGenerator.preloadQuestions()
          
          return NextResponse.json({
            success: true,
            message: 'Questions preloaded successfully',
            timestamp: new Date().toISOString()
          })
        } catch (error) {
          console.error('[Quiz API] Preload failed:', error)
          return NextResponse.json({
            success: false,
            error: 'Failed to preload questions',
            timestamp: new Date().toISOString()
          })
        }
      }
      
      case 'get_cache_stats': {
        // Get cache statistics for monitoring
        const stats = await import('@/lib/server/quizCache').then(m => m.quizCache.getStats())
        
        return NextResponse.json({
          success: true,
          stats,
          timestamp: new Date().toISOString()
        })
      }

      case 'get_socratic_followup': {
        // Generate a Socratic follow-up question based on the user's answer
        const { questionId, userAnswer, previousResponseId, questionText, category } = body
        
        // Try to find question in static data first
        let question = questionsData.questions.find(q => q.id === questionId)
        
        // If not found and it's a dynamic question, use the provided question data
        if (!question && questionId.startsWith('dynamic_')) {
          if (!questionText || !category) {
            return NextResponse.json(
              { error: 'Dynamic question data missing' },
              { status: 400 }
            )
          }
          // Create a temporary question object
          question = {
            id: questionId,
            question: questionText,
            category: category
          } as any
        }
        
        if (!question) {
          return NextResponse.json(
            { error: 'Question not found' },
            { status: 404 }
          )
        }

        // Generate Socratic follow-up using OpenAI Responses API
        const followUpResponse = await secureResponsesAgent.processHockeyIQMessage(
          `The player answered "${userAnswer}" to the question "${question.question}". Generate a Socratic follow-up.`,
          {
            category: question.category,
            age_group: 'U10',
            mode: 'socratic',
            previousResponseId  // Use native conversation tracking
          }
        )

        return NextResponse.json({
          success: true,
          followUp: followUpResponse.response,
          responseId: followUpResponse.responseId,  // Return for conversation continuity
          timestamp: new Date().toISOString()
        })
      }

      default:
        return NextResponse.json(
          { error: 'Unknown action' },
          { status: 400 }
        )
    }

  } catch (error) {
    console.error('Hockey IQ quiz error:', error)
    
    return NextResponse.json(
      { error: 'Something went wrong with the quiz' },
      { status: 500 }
    )
  }
}