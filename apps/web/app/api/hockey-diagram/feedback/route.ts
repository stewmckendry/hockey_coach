import { NextRequest, NextResponse } from 'next/server'
import { hockeyDiagramLogger } from '@/lib/server/hockeyDiagramLogger'

export async function POST(request: NextRequest) {
  try {
    const { logId, rating, categories, comment } = await request.json()
    
    // Validate input
    if (!logId || typeof logId !== 'string') {
      return NextResponse.json(
        { error: 'Log ID is required' },
        { status: 400 }
      )
    }

    if (!rating || typeof rating !== 'number' || rating < 1 || rating > 5) {
      return NextResponse.json(
        { error: 'Rating must be between 1 and 5' },
        { status: 400 }
      )
    }

    if (!Array.isArray(categories)) {
      return NextResponse.json(
        { error: 'Categories must be an array' },
        { status: 400 }
      )
    }

    // Add feedback to the log
    await hockeyDiagramLogger.addFeedback(logId, {
      rating,
      categories,
      comment: comment || ''
    })

    return NextResponse.json({
      success: true,
      message: 'Feedback recorded successfully'
    })
  } catch (error) {
    console.error('Feedback API error:', error)
    return NextResponse.json(
      { error: 'Failed to record feedback' },
      { status: 500 }
    )
  }
}