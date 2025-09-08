import { NextResponse } from 'next/server';
import questionsData from '@/data/questions.json';
import { Question } from '@/lib/types';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const period = searchParams.get('period') || '1';
    
    // Shuffle questions and select 5 per period
    const shuffled = [...questionsData.questions].sort(() => Math.random() - 0.5);
    const questionsPerPeriod = 5;
    const selectedQuestions = shuffled.slice(0, questionsPerPeriod);
    
    return NextResponse.json({
      questions: selectedQuestions,
      period: parseInt(period),
    });
  } catch (error) {
    console.error('Error fetching questions:', error);
    return NextResponse.json(
      { error: 'Failed to fetch questions' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const { count = 15 } = await request.json();
    
    // Get a mix of questions from different categories
    const allQuestions = questionsData.questions as Question[];
    const categories = ['rules-penalties', 'team-systems', 'nhl-knowledge', 'equipment-safety', 'sportsmanship'];
    const selectedQuestions: Question[] = [];
    
    // Try to get at least 2-3 questions from each category
    categories.forEach(category => {
      const categoryQuestions = allQuestions.filter(q => q.category === category);
      const shuffled = categoryQuestions.sort(() => Math.random() - 0.5);
      selectedQuestions.push(...shuffled.slice(0, 3));
    });
    
    // Shuffle final selection and return requested count
    const finalQuestions = selectedQuestions
      .sort(() => Math.random() - 0.5)
      .slice(0, count);
    
    return NextResponse.json({ questions: finalQuestions });
  } catch (error) {
    console.error('Error selecting questions:', error);
    return NextResponse.json(
      { error: 'Failed to select questions' },
      { status: 500 }
    );
  }
}