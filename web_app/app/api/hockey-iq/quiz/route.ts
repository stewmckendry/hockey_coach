import { NextRequest, NextResponse } from 'next/server'
import { secureResponsesAgent } from '@/lib/server/hockeyAgent'
import questionsData from '@/data/hockey-iq-questions.json'
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
        // Get a random question from the specified category
        const category = body.category
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
          timestamp: new Date().toISOString()
        })
      }

      case 'evaluate_answer': {
        // Evaluate user's answer using AI for flexible matching
        const { questionId, userAnswer } = body
        
        if (!questionId || !userAnswer) {
          return NextResponse.json(
            { error: 'Missing question ID or answer' },
            { status: 400 }
          )
        }

        const question = questionsData.questions.find(q => q.id === questionId)
        
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
        const { questionId, hintIndex = 0 } = body
        
        const question = questionsData.questions.find(q => q.id === questionId)
        
        if (!question) {
          return NextResponse.json(
            { error: 'Question not found' },
            { status: 404 }
          )
        }

        const hint = question.hints[Math.min(hintIndex, question.hints.length - 1)]
        
        return NextResponse.json({
          success: true,
          hint,
          hasMoreHints: hintIndex < question.hints.length - 1,
          timestamp: new Date().toISOString()
        })
      }

      case 'get_socratic_followup': {
        // Generate a Socratic follow-up question based on the user's answer
        const { questionId, userAnswer, previousResponseId } = body
        
        const question = questionsData.questions.find(q => q.id === questionId)
        
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