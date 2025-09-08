import { NextResponse } from 'next/server';
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(request: Request) {
  try {
    const { question, answer, correctAnswer, isSecondAttempt, questionType } = await request.json();

    // For multiple choice and true/false, do direct comparison
    // For short answer, use AI validation
    if (questionType === 'multiple-choice' || questionType === 'true-false' || typeof correctAnswer === 'boolean') {
      const isCorrect = String(answer).toLowerCase() === String(correctAnswer).toLowerCase();
      
      if (!isCorrect && !isSecondAttempt) {
        // Generate a hint
        const hintPrompt = `Given this hockey question for a 10-year-old: "${question}"
The correct answer is: ${correctAnswer}
The player answered incorrectly with: ${answer}

Generate a helpful hint that guides them toward the right answer without giving it away directly. Keep it simple and encouraging, suitable for a Grade 4 reading level.`;

        const hintResponse = await openai.chat.completions.create({
          model: 'gpt-4o-mini',
          messages: [{ role: 'user', content: hintPrompt }],
          max_tokens: 100,
          temperature: 0.7,
        });

        return NextResponse.json({
          correct: false,
          hint: hintResponse.choices[0].message.content,
        });
      }

      return NextResponse.json({
        correct: isCorrect,
        explanation: isCorrect 
          ? "Great job! You got it right!" 
          : `The correct answer was: ${correctAnswer}`,
      });
    }

    // For short answer questions, use AI to validate
    const validationPrompt = `You are validating answers for a youth hockey quiz for 9-10 year old kids. Be VERY generous and accepting.

Question: ${question}
Expected Answer: ${correctAnswer}
Player's Answer: ${answer}

IMPORTANT: Accept the answer as correct if:
- The core concept is right (even if wording is different)
- Common abbreviations or shorthand (e.g., "pk" for "penalty kill", "pp" for "power play")
- Minor spelling errors or typos
- Partial answers that show understanding (e.g., "offsides" instead of "offside")
- Different but valid terminology (e.g., "goalie" vs "goaltender", "sin bin" vs "penalty box")
- Numbers written as words or vice versa
- Plural/singular variations

This is for kids learning hockey - if they show they understand the concept, mark it correct!

Respond with only "true" or "false".`;

    const validationResponse = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: validationPrompt }],
      max_tokens: 10,
      temperature: 0,
    });

    const isCorrect = validationResponse.choices[0].message.content?.toLowerCase().includes('true');

    if (!isCorrect && !isSecondAttempt) {
      // Generate a hint for short answer
      const hintPrompt = `Given this hockey question for a 10-year-old: "${question}"
The correct answer is: ${correctAnswer}
The player answered incorrectly with: ${answer}

Generate a helpful hint that guides them toward the right answer without giving it away directly. Keep it simple and encouraging, suitable for a Grade 4 reading level. Maximum 2 sentences.`;

      const hintResponse = await openai.chat.completions.create({
        model: 'gpt-4o-mini',
        messages: [{ role: 'user', content: hintPrompt }],
        max_tokens: 100,
        temperature: 0.7,
      });

      return NextResponse.json({
        correct: false,
        hint: hintResponse.choices[0].message.content,
      });
    }

    return NextResponse.json({
      correct: isCorrect,
      explanation: isCorrect 
        ? "Awesome! You nailed it!" 
        : `The correct answer was: ${correctAnswer}`,
    });

  } catch (error) {
    console.error('Error validating answer:', error);
    
    // Fallback to simple string comparison if AI fails
    const { answer, correctAnswer } = await request.json();
    const isCorrect = String(answer).toLowerCase().trim() === String(correctAnswer).toLowerCase().trim();
    
    return NextResponse.json({
      correct: isCorrect,
      explanation: isCorrect ? "Correct!" : `The answer was: ${correctAnswer}`,
    });
  }
}