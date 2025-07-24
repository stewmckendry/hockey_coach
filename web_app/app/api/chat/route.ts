import { NextRequest, NextResponse } from 'next/server'
import { secureHockeyAgent } from '../../../lib/server/hockeyAgent'

// Rate limiting storage (in production, use Redis)
const rateLimitMap = new Map<string, { count: number; resetTime: number }>()

export async function POST(request: NextRequest) {
  try {
    // ✅ SECURE: Rate limiting by IP
    const clientIP = request.ip || request.headers.get('x-forwarded-for') || 'unknown'
    const now = Date.now()
    const limit = rateLimitMap.get(clientIP)
    
    if (limit && now < limit.resetTime) {
      if (limit.count >= 10) { // 10 requests per hour
        return NextResponse.json(
          { error: 'Rate limit exceeded. Please try again later.' },
          { status: 429 }
        )
      }
      limit.count++
    } else {
      rateLimitMap.set(clientIP, { count: 1, resetTime: now + 3600000 }) // 1 hour
    }

    const body = await request.json()
    
    // ✅ SECURE: Input validation
    if (!body.message || typeof body.message !== 'string') {
      return NextResponse.json(
        { error: 'Invalid message format' },
        { status: 400 }
      )
    }

    if (body.message.length > 1000) {
      return NextResponse.json(
        { error: 'Message too long' },
        { status: 400 }
      )
    }

    // Check if OpenAI API key is configured
    if (!process.env.OPENAI_API_KEY) {
      return NextResponse.json(
        { error: 'OpenAI API key not configured' },
        { status: 500 }
      )
    }

    // ✅ SECURE: Server-side processing only
    const result = await secureHockeyAgent.processMessage(
      body.message,
      body.conversationHistory || []
    )

    return NextResponse.json({
      success: true,
      response: result.response,
      metadata: result.metadata,
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('Chat API error:', error)
    
    // Return helpful error message based on error type
    let errorMessage = 'Unable to process coaching request'
    if (error instanceof Error) {
      if (error.message.includes('API key')) {
        errorMessage = 'Configuration error - please check server setup'
      } else if (error.message.includes('rate limit')) {
        errorMessage = 'Too many requests - please try again later'
      }
    }
    
    return NextResponse.json(
      { error: errorMessage },
      { status: 500 }
    )
  }
}
