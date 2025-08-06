import { NextRequest, NextResponse } from 'next/server'
import { secureResponsesAgent } from '@/lib/server/hockeyAgent'
import { hockeyIQLogger } from '@/lib/server/hockeyIQLogger'

// Simple rate limiting for Hockey IQ chatbot
const rateLimitMap = new Map<string, { count: number; resetTime: number }>()

export async function POST(request: NextRequest) {
  try {
    // Rate limiting by IP (kid-friendly: 30 requests per hour)
    const clientIP = request.ip || request.headers.get('x-forwarded-for') || 'unknown'
    const now = Date.now()
    const limit = rateLimitMap.get(clientIP)
    
    if (limit && now < limit.resetTime) {
      if (limit.count >= 30) {
        return NextResponse.json(
          { response: "Whoa! You're asking lots of questions! Take a quick break and come back in a few minutes! 🏒" },
          { status: 429 }
        )
      }
      limit.count++
    } else {
      rateLimitMap.set(clientIP, { count: 1, resetTime: now + 3600000 }) // 1 hour
    }

    const startTime = Date.now()
    const body = await request.json()
    
    // Generate session ID from IP or use provided one
    const sessionId = body.sessionId || clientIP
    
    // Validate input
    if (!body.message || typeof body.message !== 'string') {
      return NextResponse.json(
        { response: "Oops! I didn't get your question. Can you try again? 🏒" },
        { status: 400 }
      )
    }

    // Limit message length for young players
    if (body.message.length > 500) {
      return NextResponse.json(
        { response: "That's a really long question! Can you make it shorter? 😊" },
        { status: 400 }
      )
    }

    // Check OpenAI API key
    if (!process.env.OPENAI_API_KEY) {
      return NextResponse.json(
        { response: "My brain isn't working right now! Please tell your coach! 🤔" },
        { status: 500 }
      )
    }

    // Process with Hockey IQ specific handler using OpenAI Responses API
    const result = await secureResponsesAgent.processHockeyIQMessage(
      body.message,
      {
        category: body.category,
        age_group: body.age_group || 'U10',
        mode: body.mode || 'socratic',
        previousResponseId: body.previousResponseId  // Use OpenAI's native conversation tracking
      }
    )

    // Log the interaction
    await hockeyIQLogger.logChatInteraction(
      body.message,
      result.response,
      {
        responseId: result.responseId,
        previousResponseId: body.previousResponseId,
        category: body.category,
        toolsCalled: result.metadata?.toolsUsed || [],
        processingTimeMs: Date.now() - startTime,
        sessionId,
        ipAddress: clientIP
      }
    )

    return NextResponse.json({
      success: true,
      response: result.response,
      responseId: result.responseId,  // Return for next conversation turn
      metadata: result.metadata,
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('Hockey IQ chat error:', error)
    
    // Log the error
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    await hockeyIQLogger.logChatInteraction(
      body?.message || 'Unknown message',
      'Error occurred',
      {
        processingTimeMs: Date.now() - startTime,
        sessionId: body?.sessionId || clientIP,
        ipAddress: clientIP,
        error: errorMessage
      }
    )
    
    return NextResponse.json(
      { response: "Something went wrong! Let's try that again! 🏒" },
      { status: 500 }
    )
  }
}