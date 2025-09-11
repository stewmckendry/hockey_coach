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

// Add harder questions for U10 players
const additionalHardQuestions: Question[] = [
  {
    id: "advanced-1",
    category: "team-tactics",
    type: "multiple-choice",
    question: "In a box penalty kill formation, how many players form the 'box'?",
    options: ["2", "3", "4", "5"],
    correctAnswer: "4",
    hint: "It's called a 'box' for a reason - think about the shape!",
    explanation: "Four penalty killers form a box shape to protect the slot area."
  },
  {
    id: "advanced-2",
    category: "team-tactics",
    type: "multiple-choice",
    question: "What's the advantage of a 5-on-3 power play?",
    options: ["More ice time", "Two extra attackers", "No offsides", "Bigger net"],
    correctAnswer: "Two extra attackers",
    hint: "Count the difference in players!",
    explanation: "5-on-3 means you have two more attackers than defenders, creating lots of space."
  },
  {
    id: "advanced-3",
    category: "rules-penalties",
    type: "multiple-choice",
    question: "What type of penalty results in a player being ejected from the game?",
    options: ["Minor", "Major", "Match", "Bench minor"],
    correctAnswer: "Match",
    hint: "It 'matches' the severity - you're out!",
    explanation: "A match penalty means immediate ejection from the game."
  },
  {
    id: "advanced-4",
    category: "team-tactics",
    type: "short-answer",
    question: "In a diamond penalty kill, the formation looks like what shape?",
    correctAnswer: "diamond",
    hint: "The answer is in the name!",
    explanation: "The diamond PK has one player up high, two in the middle, and one low."
  },
  {
    id: "advanced-5",
    category: "rules-penalties",
    type: "true-false",
    question: "A team can 'pull' their goalie to add an extra attacker even when not behind.",
    correctAnswer: true,
    hint: "Strategy isn't just for when you're losing!",
    explanation: "Teams can pull the goalie anytime, like on a delayed penalty call."
  },
  {
    id: "advanced-6",
    category: "team-tactics",
    type: "multiple-choice",
    question: "What's a 'wedge' penalty kill designed to do?",
    options: ["Block all shots", "Force play to one side", "Protect the goalie", "Create offense"],
    correctAnswer: "Force play to one side",
    hint: "Think about what a wedge shape does - it splits things!",
    explanation: "The wedge PK uses a triangle to force the power play to one side of the ice."
  },
  {
    id: "advanced-7",
    category: "skills-fundamentals",
    type: "multiple-choice",
    question: "What's a 'Michigan' move in hockey?",
    options: ["A type of check", "Lacrosse-style goal", "Spin move", "Between legs pass"],
    correctAnswer: "Lacrosse-style goal",
    hint: "It's named after a university team that made it famous!",
    explanation: "The Michigan is when you scoop the puck on your stick like lacrosse and score."
  },
  {
    id: "advanced-8",
    category: "nhl-knowledge",
    type: "multiple-choice",
    question: "Which NHL trophy is awarded to the best defensive forward?",
    options: ["Hart Trophy", "Selke Trophy", "Norris Trophy", "Vezina Trophy"],
    correctAnswer: "Selke Trophy",
    hint: "It's not for defensemen, but for forwards who play great defense!",
    explanation: "The Frank J. Selke Trophy goes to the forward with the best defensive skills."
  },
  {
    id: "advanced-9",
    category: "rules-penalties",
    type: "multiple-choice",
    question: "How many minutes is a double minor penalty?",
    options: ["2", "4", "5", "10"],
    correctAnswer: "4",
    hint: "It's double a regular minor!",
    explanation: "A double minor is 4 minutes (2+2), often given for high-sticking that draws blood."
  },
  {
    id: "advanced-10",
    category: "team-tactics",
    type: "true-false",
    question: "In a 1-3-1 power play, there are three players across the middle of the zone.",
    correctAnswer: true,
    hint: "The numbers tell you the formation!",
    explanation: "1-3-1 means 1 up high, 3 across the middle, and 1 down low."
  },
  {
    id: "advanced-11",
    category: "rules-penalties",
    type: "short-answer",
    question: "A penalty shot is awarded when a player is fouled on a _______.",
    correctAnswer: "breakaway",
    hint: "When you're all alone with the goalie!",
    explanation: "Penalty shots are awarded when fouled on a clear breakaway opportunity."
  },
  {
    id: "advanced-12",
    category: "skills-fundamentals",
    type: "multiple-choice",
    question: "What's the 'Forsberg move' named after Peter Forsberg?",
    options: ["Spin-o-rama", "One-handed deke", "Between-the-legs", "Fake shot pass"],
    correctAnswer: "One-handed deke",
    hint: "He did it in the Olympics with one hand on his stick!",
    explanation: "The Forsberg is a one-handed deke move made famous in shootouts."
  },
  {
    id: "advanced-13",
    category: "team-tactics",
    type: "multiple-choice",
    question: "What does 'cycling' mean in the offensive zone?",
    options: ["Spinning in circles", "Passing along the boards", "Changing lines quickly", "Skating backwards"],
    correctAnswer: "Passing along the boards",
    hint: "The puck moves in a cycle pattern!",
    explanation: "Cycling means moving the puck along the boards to maintain possession."
  },
  {
    id: "advanced-14",
    category: "nhl-knowledge",
    type: "multiple-choice",
    question: "What's a 'Gordie Howe hat trick'?",
    options: ["3 goals", "Goal, assist, and fight", "3 assists", "Shutout game"],
    correctAnswer: "Goal, assist, and fight",
    hint: "Named after 'Mr. Hockey' who could do it all!",
    explanation: "A Gordie Howe hat trick is scoring a goal, an assist, and getting in a fight."
  },
  {
    id: "advanced-15",
    category: "rules-penalties",
    type: "true-false",
    question: "Too many men on the ice is always a 2-minute penalty, even in overtime.",
    correctAnswer: true,
    hint: "The rules don't change for this one!",
    explanation: "Too many men is always a 2-minute minor penalty, regardless of game situation."
  }
];

// Questions that are too easy for U10 (to be removed)
const tooEasyQuestionIds = [
  "equipment-2", // "Hockey players wear helmets" - too obvious
  "sportsmanship-2", // "It's okay to yell at teammates" - too simple
  "sportsmanship-4", // "What do we say to referees" - too basic
  "thunder-systems-2", // "Stay between your man and net" - already covered better
  "skills-2", // "Keep knees straight when stopping" - too basic
  "drills-2", // "Station practices help focus" - too obvious
];

async function enrichQuestionsV2() {
  // Load existing questions
  const questionsPath = path.join(__dirname, '..', 'data', 'questions.json');
  const questionsData = JSON.parse(fs.readFileSync(questionsPath, 'utf-8'));
  let questions: Question[] = questionsData.questions;

  // Note: harder questions already added to questions.json, so don't add duplicates

  // Filter out too-easy questions
  questions = questions.filter(q => !tooEasyQuestionIds.includes(q.id));

  console.log(`Enriching ${questions.length} questions with better difficulty calibration...`);

  const enrichedQuestions = [];

  // Process in batches
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
                
                IMPORTANT: Be strict about difficulty ratings. Most U10 players:
                - Know basic rules (offsides, icing, penalties)
                - Are learning team systems and positioning
                - Have limited knowledge of advanced tactics
                
                Difficulty ratings:
                - EASY: Very basic concepts that most U10 players already know
                  Examples: How many players on ice? What's a goal? Basic equipment names
                  These should be RARE - most questions are NOT easy for U10!
                
                - MEDIUM: Age-appropriate challenges that require some hockey knowledge
                  Examples: What's icing? Penalty lengths, basic positions, team systems
                  Most questions should be medium!
                
                - HARD: Advanced concepts that challenge even experienced U10 players
                  Examples: Special teams tactics, complex rules, NHL trivia, advanced moves
                  Penalty kill formations, power play setups, advanced dekes
                
                Topic tags (2-3 topics) from:
                - rules: Basic game rules and penalties
                - positions: Player positions and responsibilities
                - equipment: Gear and safety equipment
                - nhl: NHL teams, players, history
                - strategy: Game tactics and plays
                - skills: Skating, passing, shooting techniques
                - sportsmanship: Fair play and teamwork
                - safety: Safety rules and protocols
                - team-systems: Team-specific plays and formations
                - special-teams: Power play and penalty kill
                
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
                category: q.category,
                questionId: q.id
              })
            }
          ],
          temperature: 0.3,
          response_format: { type: "json_object" }
        });

        const enrichment = JSON.parse(response.choices[0].message.content || '{}');
        
        // Special handling for known hard questions
        const hardQuestionKeywords = ['penalty kill', 'power play', 'box formation', 'diamond', 'wedge', 
                                      'cycling', 'Gordie Howe', 'Selke', 'Michigan', 'Forsberg', 
                                      'double minor', 'match penalty', '5-on-3', '1-3-1'];
        
        const isHardQuestion = hardQuestionKeywords.some(keyword => 
          q.question.toLowerCase().includes(keyword.toLowerCase())
        );
        
        return {
          ...q,
          difficulty: isHardQuestion ? 'hard' : (enrichment.difficulty || 'medium'),
          topics: enrichment.topics || [q.category],
          ageAppropriate: enrichment.ageAppropriate !== false,
          estimatedReadingTime: enrichment.estimatedReadingTime || 10,
          hint: enrichment.improvedHint || q.hint || `Think about ${q.category.replace('-', ' ')}`,
          explanation: q.explanation || enrichment.explanation
        };
      } catch (error) {
        console.error(`Error enriching question ${q.id}:`, error);
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
  console.log('\nTotal Questions:', enrichedQuestions.length);

  // Save enriched questions
  const outputPath = path.join(__dirname, '..', 'data', 'questions.json');
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
  console.log('Questions are ready for use!');
}

// Run enrichment
enrichQuestionsV2().catch(console.error);