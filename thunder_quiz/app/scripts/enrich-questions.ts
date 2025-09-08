import fs from 'fs';
import path from 'path';
import OpenAI from 'openai';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config({ path: path.join(__dirname, '..', '.env') });

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

interface Question {
  id: string;
  category: string;
  type: string;
  question: string;
  options?: string[];
  correctAnswer: string | boolean;
  hint?: string;
  explanation?: string;
  difficulty?: "easy" | "medium" | "hard";
  topics?: string[];
  ageAppropriate?: boolean;
  estimatedReadingTime?: number;
}

async function enrichQuestions() {
  // Load existing questions
  const questionsPath = path.join(__dirname, '..', 'data', 'questions.json');
  const questionsData = JSON.parse(fs.readFileSync(questionsPath, 'utf-8'));
  const questions: Question[] = questionsData.questions;

  console.log(`Enriching ${questions.length} questions...`);

  const enrichedQuestions = [];

  // Process in batches to avoid rate limits
  const batchSize = 10;
  for (let i = 0; i < questions.length; i += batchSize) {
    const batch = questions.slice(i, i + batchSize);
    
    const enrichmentPromises = batch.map(async (q) => {
      try {
        const response = await openai.chat.completions.create({
          model: 'gpt-4o-mini',
          messages: [
            {
              role: 'system',
              content: `You are a hockey education expert evaluating questions for 9-10 year old players (U10 level).
                
                Analyze each question and provide:
                1. Difficulty rating (easy/medium/hard) based on:
                   - Easy: Basic rules, simple concepts, yes/no questions
                   - Medium: Game situations, basic strategy, requires some hockey knowledge
                   - Hard: Complex rules, advanced concepts, specific NHL knowledge
                
                2. Topic tags (2-3 topics) from:
                   - rules: Basic game rules and penalties
                   - positions: Player positions and responsibilities
                   - equipment: Gear and safety equipment
                   - nhl: NHL teams, players, history
                   - strategy: Game tactics and plays
                   - skills: Skating, passing, shooting techniques
                   - sportsmanship: Fair play and teamwork
                   - safety: Safety rules and protocols
                
                3. Age appropriateness (true/false)
                4. Estimated reading time in seconds for a grade 4 student
                5. Improved hint if the current one is too vague or missing
                
                Return JSON only.`
            },
            {
              role: 'user',
              content: JSON.stringify({
                question: q.question,
                type: q.type,
                options: q.options,
                correctAnswer: q.correctAnswer,
                currentHint: q.hint,
                category: q.category
              })
            }
          ],
          temperature: 0.3,
          response_format: { type: "json_object" }
        });

        const enrichment = JSON.parse(response.choices[0].message.content || '{}');
        
        return {
          ...q,
          difficulty: enrichment.difficulty || 'medium',
          topics: enrichment.topics || [q.category],
          ageAppropriate: enrichment.ageAppropriate !== false,
          estimatedReadingTime: enrichment.estimatedReadingTime || 10,
          hint: enrichment.improvedHint || q.hint || `Think about ${q.category.replace('-', ' ')}`,
          explanation: q.explanation || enrichment.explanation
        };
      } catch (error) {
        console.error(`Error enriching question ${q.id}:`, error);
        // Fallback enrichment
        return {
          ...q,
          difficulty: 'medium',
          topics: [q.category],
          ageAppropriate: true,
          estimatedReadingTime: 10
        };
      }
    });

    const batchResults = await Promise.all(enrichmentPromises);
    enrichedQuestions.push(...batchResults);
    
    console.log(`Processed ${Math.min(i + batchSize, questions.length)}/${questions.length} questions`);
    
    // Small delay between batches to avoid rate limits
    if (i + batchSize < questions.length) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  // Analyze distribution
  const difficultyCount = { easy: 0, medium: 0, hard: 0 };
  const topicCount: Record<string, number> = {};
  
  enrichedQuestions.forEach(q => {
    difficultyCount[q.difficulty as keyof typeof difficultyCount]++;
    q.topics?.forEach((topic: string) => {
      topicCount[topic] = (topicCount[topic] || 0) + 1;
    });
  });

  console.log('\nDifficulty Distribution:');
  console.log(difficultyCount);
  console.log('\nTopic Distribution:');
  console.log(topicCount);

  // Save enriched questions
  const outputPath = path.join(__dirname, '..', 'data', 'questions-enriched.json');
  fs.writeFileSync(outputPath, JSON.stringify({
    questions: enrichedQuestions,
    metadata: {
      totalQuestions: enrichedQuestions.length,
      difficultyDistribution: difficultyCount,
      topicDistribution: topicCount,
      enrichedAt: new Date().toISOString()
    }
  }, null, 2));

  console.log(`\nEnriched questions saved to ${outputPath}`);
  console.log('Next step: Review enriched questions and rename to questions.json when ready');
}

// Run enrichment
enrichQuestions().catch(console.error);