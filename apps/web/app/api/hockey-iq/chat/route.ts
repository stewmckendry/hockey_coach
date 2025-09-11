import { NextRequest, NextResponse } from 'next/server'
import { secureResponsesAgent } from '@/lib/server/hockeyAgent'
import { hockeyIQLogger } from '@/lib/server/hockeyIQLogger'
import { SessionManager } from '@/lib/server/sessionManager'
import { monitorStorage } from '@/lib/server/monitorStorage'

// Simple rate limiting for Hockey IQ chatbot
const rateLimitMap = new Map<string, { count: number; resetTime: number }>()

export async function POST(request: NextRequest) {
  const clientIP = request.ip || request.headers.get('x-forwarded-for') || 'unknown'
  const startTime = Date.now()
  let body: any = {}  // Declare body outside try block for error handling
  
  try {
    // Rate limiting by IP (kid-friendly: 30 requests per hour)
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

    body = await request.json()
    
    // Extract session information from request
    const sessionInfo = SessionManager.extractSessionInfo(request)
    const sessionId = body.sessionId || sessionInfo.sessionId
    
    // Initialize or update session tracking
    SessionManager.createOrUpdateSession(sessionId, clientIP, sessionInfo.userAgent, 'chat')
    
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
    
    // Add to session tracking
    SessionManager.logChatInteraction({
      sessionId: sessionId,
      messageId: result.responseId || `msg_${Date.now()}`,
      responseId: result.responseId || `resp_${Date.now()}`,
      question: body.message,
      response: result.response,
      processingTime: Date.now() - startTime,
      toolsUsed: result.metadata?.toolsUsed || [],
      category: body.category || 'general',
      ageGroup: body.age_group || 'U10',
      mode: body.mode || 'qa',
      timestamp: new Date().toISOString()
    })
    
    // Save to persistent storage
    monitorStorage.saveSession(SessionManager.getSession(sessionId)!)
    
    // Save chat interactions to persistent storage
    const chatInteractions = SessionManager.getChatInteractions(sessionId)
    const allInteractions = monitorStorage.loadChatInteractions()
    allInteractions[sessionId] = chatInteractions
    monitorStorage.saveChatInteractions(allInteractions)

    // Create response with session cookie
    const response = NextResponse.json({
      success: true,
      response: result.response,
      responseId: result.responseId,  // Return for next conversation turn
      metadata: result.metadata,
      sessionId: sessionId,  // Return session ID for client tracking
      timestamp: new Date().toISOString()
    })
    
    // Set session cookie for browser tracking (always update to ensure valid format)
    response.cookies.set('hockey-iq-session', sessionId, {
      maxAge: 60 * 60 * 24 * 7, // 7 days
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/'  // Ensure cookie is available site-wide
    })
    
    return response

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