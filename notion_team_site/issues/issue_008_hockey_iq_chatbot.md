# Issue #8: Implement Hockey IQ Chatbot

## Overview
Create an interactive Hockey IQ chatbot that uses Socratic-style questioning to help U10 players learn hockey concepts in a fun, engaging way. The chatbot will be embedded in the Notion team site.

## Objectives
- Design age-appropriate hockey questions
- Use Socratic method to guide learning
- Make learning fun and interactive
- Build hockey knowledge progressively
- Track player engagement (optional)

## Chatbot Design

### Core Features
1. **Question Categories**
   - Rules & Penalties
   - Positioning & Strategy
   - Skills & Techniques
   - Teamwork & Sportsmanship
   - Hockey History & Fun Facts

2. **Question Difficulty Levels**
   - Rookie (basic concepts)
   - Player (intermediate understanding)
   - All-Star (advanced for age group)

3. **Response Style**
   - Encouraging regardless of answer
   - Guides to correct answer through hints
   - Celebrates learning, not just correct answers

### Socratic Method Implementation
Instead of just asking questions, the bot:
- Asks "Why do you think that?"
- Provides hints through follow-up questions
- Relates concepts to player experiences
- Encourages deeper thinking

## Question Bank Examples

### Rules & Penalties
**Rookie Question**: "What happens when the puck goes over the glass in the defensive zone?"
- If correct: "Great job! Why do you think that rule exists?"
- If incorrect: "Good try! Here's a hint: Is it a penalty or a face-off?"

**Player Question**: "When can a player be offside?"
- Follow-up: "Why does the offside rule help make hockey fair?"

### Positioning & Strategy
**Rookie Question**: "Where should the center be during a face-off?"
- Visual hint option: Show rink diagram
- Follow-up: "What's the center's first job after winning the face-off?"

**Player Question**: "Your team is on a power play. Where's a good place for a defender to stand?"
- Guide: "Think about having a good shot and seeing the whole ice..."

### Skills & Techniques  
**Rookie Question**: "What part of your stick blade should touch the puck for a good pass?"
- Hint: "Is it the toe, middle, or heel?"
- Follow-up: "Why does that give you better control?"

### Teamwork & Sportsmanship
**All Questions**: "Your teammate made a mistake that led to a goal. What should you do?"
- Always guide toward supportive responses
- Discuss why teamwork matters

## Technical Implementation

### Architecture Options

#### Option 1: Notion AI Integration
```javascript
// Notion AI widget approach
const HockeyIQBot = {
  questionBank: loadQuestions(),
  currentQuestion: null,
  
  async askQuestion(category, level) {
    const question = this.selectQuestion(category, level);
    return this.formatForNotion(question);
  },
  
  async processAnswer(answer) {
    // Use Claude API to evaluate and respond
    const response = await evaluateAnswer(answer);
    return this.generateSocraticFollowUp(response);
  }
}
```

#### Option 2: Embedded Widget
- Create standalone web component
- Embed in Notion via iframe
- Host on Vercel/Netlify

#### Option 3: Notion Database-Driven
- Questions stored in Notion database
- Synced blocks for Q&A flow
- Manual but simpler implementation

### Question Database Structure
```typescript
interface HockeyQuestion {
  id: string;
  category: QuestionCategory;
  level: 'rookie' | 'player' | 'all-star';
  question: string;
  correctAnswer: string;
  hints: string[];
  followUpQuestions: string[];
  funFact?: string;
  visualAid?: string; // URL to diagram
  ageGroup: 'U10';
}
```

### Response Logic
```typescript
function generateResponse(isCorrect: boolean, attempt: number): string {
  if (isCorrect) {
    return getEncouragingMessage() + getFollowUpQuestion();
  } else {
    if (attempt === 1) {
      return "Good thinking! " + getHint(1);
    } else {
      return "Almost there! " + getHint(2) + showVisualAid();
    }
  }
}
```

## User Experience Design

### Chat Interface
```
🏒 Hockey IQ Coach: "Hi! I'm here to help you become a hockey genius! What would you like to learn about today?"

[Rules] [Positions] [Skills] [Teamwork] [Fun Facts]

Player: *clicks Skills*

🏒 Hockey IQ Coach: "Awesome choice! Here's a question about skills:
When you're skating backward, which way should your toes point?"

[Multiple choice buttons or text input]
```

### Progress Tracking (Optional)
- Stars earned for categories completed
- "Hockey IQ Level" badge system
- Fun achievements ("Penalty Box Expert", "Positioning Pro")

## Content Creation

### Question Development Process
1. Research age-appropriate concepts
2. Write questions in kid-friendly language
3. Create 2-3 hints per question
4. Design follow-up questions
5. Add fun facts and encouragement

### Initial Question Bank
- 10 questions per category
- 5 categories = 50 total questions
- Mix of difficulty levels
- Include seasonal/timely questions

## Integration with Notion

### Embedding Options
1. **Notion Synced Blocks**: Update question of the day
2. **Third-party Widgets**: Typeform, Tally, etc.
3. **Custom Integration**: Via Notion API
4. **Simple Solution**: Linked Google Form quiz

### Placement on Site
- Dedicated "Hockey IQ Zone" page
- Widget on team homepage
- Practice plan integration
- Mobile-friendly design

## Success Criteria
- [ ] 50+ questions created
- [ ] Socratic method implemented
- [ ] Integration with Notion working
- [ ] Mobile-responsive design
- [ ] Positive, encouraging tone
- [ ] Age-appropriate content
- [ ] Fun and engaging experience

## Future Enhancements
- Voice interaction option
- Multiplayer quiz mode
- Parent-child challenge mode
- Integration with practice attendance
- Seasonal question updates
- Video question support

## Notes
- Keep questions short (1-2 sentences)
- Always encourage effort over accuracy
- Include diverse player representations
- Make wrong answers learning opportunities
- Celebrate curiosity and questions