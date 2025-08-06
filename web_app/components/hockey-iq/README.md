# 🏒 Hockey IQ Chatbot

An interactive dual-mode chatbot designed for U10 hockey players (8-9 years old) that uses Socratic questioning to teach hockey concepts in a fun, engaging way.

## Features

### Two Modes of Learning

1. **Q&A Mode** 💬
   - Players ask questions about hockey
   - Bot responds with Socratic reasoning
   - Guides learning through follow-up questions
   - Integrates with hockey MCP knowledge base

2. **Quiz Mode** 🎯
   - Bot asks questions from curated question bank
   - Progressive hints after wrong answers
   - Encouraging feedback regardless of accuracy
   - Fun facts and follow-up questions

### Age-Appropriate Design
- Grade 3-4 reading level
- 70% visual, 30% text ratio (per UX guidelines)
- Large, colorful buttons
- Emoji feedback and rewards
- Achievement system with badges

## Usage

### Direct Access
```
http://localhost:3000/hockey-iq
```

### Notion Embedding
Embed as an iframe in Notion:
```html
<iframe src="http://localhost:3000/hockey-iq?embedded=true" 
        width="100%" 
        height="600px" 
        frameborder="0">
</iframe>
```

Or use Notion's embed block:
1. Type `/embed` in Notion
2. Paste URL: `http://localhost:3000/hockey-iq?embedded=true`
3. Adjust height as needed

## Question Bank

20+ questions across 5 categories:
- **Rules & Penalties** ⚖️
- **Positioning & Strategy** 🎯
- **Skills & Techniques** 🏒
- **Teamwork & Sportsmanship** 🤝
- **Hockey History & Fun Facts** ⭐

Each question includes:
- Correct answer
- 2-3 progressive hints
- Follow-up questions
- Encouraging messages
- Fun facts (where applicable)

## API Endpoints

### Chat API
`POST /api/hockey-iq/chat`
```json
{
  "message": "What's offside?",
  "category": "rules",
  "age_group": "U10",
  "mode": "socratic"
}
```

### Quiz API
`POST /api/hockey-iq/quiz`
```json
{
  "action": "get_question",
  "category": "skills"
}
```

Actions:
- `get_question` - Get random question
- `evaluate_answer` - Check user's answer
- `get_hint` - Get next hint
- `get_socratic_followup` - Generate follow-up

## Technical Architecture

### Components
- `HockeyIQInterface.tsx` - Main container
- `ModeSelector.tsx` - Q&A/Quiz toggle
- `QuizQuestion.tsx` - Quiz display
- `KidFriendlyChat.tsx` - Chat interface

### Integration
- Uses existing chat infrastructure
- Leverages hockey MCP tools for knowledge
- OpenAI API for Socratic reasoning
- Responsive design with Tailwind CSS

## Socratic Method Implementation

The bot uses guided questioning instead of direct answers:

**Example:**
```
Player: "What's a hat trick?"
Bot: "Great question! 🏒 Let's think about it... Have you ever seen fans throw something on the ice when a player does something special? What number do you think is important for a hat trick? Here's a hint: it's less than 5 but more than 1!"
```

## Achievement System

Players can unlock achievements:
- **First Goal!** 🥅 - First correct answer
- **Hat Trick Hero** 🎩 - 5 correct in a row
- **Category Champion** 🏆 - Complete a category
- **Curious Coach** 🤔 - Ask 5 questions

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_api_key  # Required for AI responses
```

### Customization
Edit `data/hockey-iq-questions.json` to:
- Add new questions
- Modify categories
- Update achievements
- Change difficulty levels

## Development

### Adding Questions
```json
{
  "id": "unique_id",
  "category": "rules|positioning|skills|teamwork|fun_facts",
  "level": "rookie|player|all-star",
  "question": "Your question here?",
  "correctAnswer": "The correct answer",
  "hints": ["First hint", "Second hint"],
  "followUpQuestions": ["Why do you think...?"],
  "encouragementMessages": {
    "correct": "Great job!",
    "incorrect": "Keep trying!"
  },
  "funFact": "Optional fun fact"
}
```

### Testing
```bash
# Start the development server
npm run dev

# Access Hockey IQ
http://localhost:3000/hockey-iq

# Test embedding
http://localhost:3000/hockey-iq?embedded=true
```

## Best Practices

### Content Guidelines
- Keep questions under 2 sentences
- Use familiar hockey terms for U10
- Always be encouraging
- Celebrate effort over accuracy
- Include visual references when possible

### Socratic Questioning
- Start with "Why do you think...?"
- Break complex ideas into steps
- Relate to player experiences
- Use concrete examples
- End with encouragement

## Future Enhancements
- Voice interaction support
- Multiplayer quiz mode
- Progress tracking/accounts
- Parent viewing mode
- More questions and categories
- Video integration
- Seasonal updates

## Support

For issues or questions about the Hockey IQ Chatbot, please refer to the main project documentation or contact the development team.