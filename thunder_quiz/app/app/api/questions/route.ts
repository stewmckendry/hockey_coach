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
    
    // Get all questions with difficulty ratings
    const allQuestions = questionsData.questions as Question[];
    
    // Progressive difficulty: Period 1 = Easy, Period 2 = Medium, Period 3 = Hard
    // 5 questions per period for standard game
    const easyQuestions = allQuestions.filter(q => q.difficulty === 'easy');
    const mediumQuestions = allQuestions.filter(q => q.difficulty === 'medium');
    const hardQuestions = allQuestions.filter(q => q.difficulty === 'hard');
    
    // Proper Fisher-Yates shuffle for true randomization
    const shuffleArray = (arr: Question[]) => {
      const shuffled = [...arr];
      for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
      }
      return shuffled;
    };
    
    // Function to select questions with topic diversity
    const selectDiverseQuestions = (questions: Question[], numToSelect: number): Question[] => {
      const selected: Question[] = [];
      const usedCategories = new Set<string>();
      const usedTopics = new Set<string>();
      
      // Shuffle the input questions
      const shuffled = shuffleArray(questions);
      
      // First pass: try to get diverse categories
      for (const q of shuffled) {
        if (selected.length >= numToSelect) break;
        
        // Prefer questions from unused categories
        if (!usedCategories.has(q.category)) {
          selected.push(q);
          usedCategories.add(q.category);
          if (q.topics) {
            q.topics.forEach(t => usedTopics.add(t));
          }
        }
      }
      
      // Second pass: fill remaining slots, prioritizing topic diversity
      for (const q of shuffled) {
        if (selected.length >= numToSelect) break;
        if (selected.includes(q)) continue;
        
        // Calculate topic overlap score (lower is better)
        const overlapScore = q.topics 
          ? q.topics.filter(t => usedTopics.has(t)).length 
          : 0;
        
        // Add questions with minimal topic overlap
        if (overlapScore <= 1) {
          selected.push(q);
          usedCategories.add(q.category);
          if (q.topics) {
            q.topics.forEach(t => usedTopics.add(t));
          }
        }
      }
      
      // Final pass: if still need more, just add what's left
      for (const q of shuffled) {
        if (selected.length >= numToSelect) break;
        if (!selected.includes(q)) {
          selected.push(q);
        }
      }
      
      return selected;
    };
    
    const selectedQuestions: Question[] = [];
    
    // Period 1: Mix of easy and easier medium questions (since we only have 15 easy)
    const period1Easy = selectDiverseQuestions(easyQuestions, 3);
    const period1Medium = selectDiverseQuestions(mediumQuestions, 2);
    selectedQuestions.push(...period1Easy, ...period1Medium);
    
    // Period 2: Mostly medium with some easy
    const remainingMedium = mediumQuestions.filter(q => !selectedQuestions.includes(q));
    const period2Medium = selectDiverseQuestions(remainingMedium, 3);
    const remainingEasy = easyQuestions.filter(q => !selectedQuestions.includes(q));
    const period2Easy = selectDiverseQuestions(remainingEasy, 2);
    selectedQuestions.push(...period2Medium, ...period2Easy);
    
    // Period 3: Mix of hard and medium
    const period3Hard = selectDiverseQuestions(hardQuestions, 3);
    const remainingMediumForP3 = mediumQuestions.filter(q => !selectedQuestions.includes(q));
    const period3Medium = selectDiverseQuestions(remainingMediumForP3, 2);
    selectedQuestions.push(...period3Hard, ...period3Medium);
    
    // If we need more questions (overtime), mix medium and hard with diversity
    if (count > 15) {
      const remainingHard = hardQuestions.filter(q => !selectedQuestions.includes(q));
      const remainingMediumForOT = mediumQuestions.filter(q => !selectedQuestions.includes(q));
      const overtimePool = [...remainingHard, ...remainingMediumForOT];
      const overtimeQuestions = selectDiverseQuestions(overtimePool, count - 15);
      selectedQuestions.push(...overtimeQuestions);
    }
    
    return NextResponse.json({ questions: selectedQuestions.slice(0, count) });
  } catch (error) {
    console.error('Error selecting questions:', error);
    return NextResponse.json(
      { error: 'Failed to select questions' },
      { status: 500 }
    );
  }
}