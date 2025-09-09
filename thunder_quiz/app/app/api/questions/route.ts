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
    const { count = 15, recentlyUsedIds = [] } = await request.json();
    
    // Get all questions with difficulty ratings
    const allQuestions = questionsData.questions as Question[];
    
    // Track recently used questions (from client's session storage)
    const recentlyUsedSet = new Set(recentlyUsedIds);
    
    // Proper Fisher-Yates shuffle for true randomization
    const shuffleArray = (arr: Question[]) => {
      const shuffled = [...arr];
      for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
      }
      return shuffled;
    };
    
    // Enhanced selection with better repeat prevention
    const selectQuestionsWithMemory = (
      questions: Question[], 
      numToSelect: number,
      alreadySelected: Set<string>
    ): Question[] => {
      const selected: Question[] = [];
      const usedCategories = new Set<string>();
      
      // Separate into unused and recently used
      const unused = questions.filter(q => !recentlyUsedSet.has(q.id) && !alreadySelected.has(q.id));
      const recentlyUsed = questions.filter(q => recentlyUsedSet.has(q.id) && !alreadySelected.has(q.id));
      
      // Shuffle both pools
      const shuffledUnused = shuffleArray(unused);
      const shuffledRecent = shuffleArray(recentlyUsed);
      
      // First: Select from unused questions with category diversity
      for (const q of shuffledUnused) {
        if (selected.length >= numToSelect) break;
        
        // Prioritize category diversity
        if (!usedCategories.has(q.category) || selected.length < numToSelect / 2) {
          selected.push(q);
          usedCategories.add(q.category);
          alreadySelected.add(q.id);
        }
      }
      
      // Second: Fill remaining from unused without category restriction
      for (const q of shuffledUnused) {
        if (selected.length >= numToSelect) break;
        if (!selected.includes(q)) {
          selected.push(q);
          alreadySelected.add(q.id);
        }
      }
      
      // Last resort: Use recently used questions if needed
      for (const q of shuffledRecent) {
        if (selected.length >= numToSelect) break;
        selected.push(q);
        alreadySelected.add(q.id);
      }
      
      return selected;
    };
    
    const selectedQuestions: Question[] = [];
    const alreadySelectedIds = new Set<string>();
    
    // More balanced difficulty distribution (less reliance on limited easy questions)
    // Period 1: Easier questions (easy + easier mediums)
    const easyQuestions = allQuestions.filter(q => q.difficulty === 'easy');
    const mediumQuestions = allQuestions.filter(q => q.difficulty === 'medium');
    const hardQuestions = allQuestions.filter(q => q.difficulty === 'hard');
    
    // Period 1: Easy and medium (2 easy, 3 medium)
    const period1Easy = selectQuestionsWithMemory(easyQuestions, 2, alreadySelectedIds);
    const period1Medium = selectQuestionsWithMemory(mediumQuestions, 3, alreadySelectedIds);
    selectedQuestions.push(...shuffleArray([...period1Easy, ...period1Medium]));
    
    // Period 2: Medium-hard (2 medium, 3 hard)
    const period2Medium = selectQuestionsWithMemory(mediumQuestions, 2, alreadySelectedIds);
    const period2Hard = selectQuestionsWithMemory(hardQuestions, 3, alreadySelectedIds);
    selectedQuestions.push(...shuffleArray([...period2Medium, ...period2Hard]));
    
    // Period 3: Hard only (5 hard)
    const period3Hard = selectQuestionsWithMemory(hardQuestions, 5, alreadySelectedIds);
    selectedQuestions.push(...shuffleArray(period3Hard));
    
    // Overtime: Mix of medium and hard
    if (count > 15) {
      const overtimeQuestions: Question[] = [];
      for (let i = 15; i < count; i++) {
        // Alternate between medium and hard for overtime
        const pool = i % 2 === 0 ? mediumQuestions : hardQuestions;
        const selected = selectQuestionsWithMemory(pool, 1, alreadySelectedIds);
        overtimeQuestions.push(...selected);
      }
      selectedQuestions.push(...overtimeQuestions);
    }
    
    return NextResponse.json({ 
      questions: selectedQuestions.slice(0, count),
      totalQuestionsInPool: allQuestions.length
    });
  } catch (error) {
    console.error('Error selecting questions:', error);
    return NextResponse.json(
      { error: 'Failed to select questions' },
      { status: 500 }
    );
  }
}