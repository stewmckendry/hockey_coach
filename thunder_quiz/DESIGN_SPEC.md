# Thunder Hockey Quiz App - Design Specification

## 🏒 Project Overview
Interactive hockey quiz application for U10A Ted Reeve Thunder team, designed to be embedded directly in their Notion team site for player engagement and learning.

**Team Notion Site**: https://www.notion.so/U10A-Ted-Reeves-Thunder-2660cdbf49778099a6bbccfc949f854b

## 👤 User Requirements

### Target Audience
- **Primary Users**: U10A hockey players (ages 9-10, Grade 4)
- **Secondary Users**: Parents and coaches monitoring progress
- **Access Point**: Embedded directly in team Notion site

### User Stories
1. **As a player**, I want to test my hockey knowledge in a fun game format
2. **As a player**, I want to compete for high scores on the team leaderboard
3. **As a player**, I want hints when I get questions wrong to help me learn
4. **As a coach**, I want players to learn team systems through engaging repetition
5. **As a parent**, I want age-appropriate content my child can navigate independently

## 🎮 Functional Requirements

### Core Game Flow
1. **Session Start**
   - Player enters nickname (alphanumeric, 3-15 characters)
   - Nickname used only for leaderboard display
   - No authentication required

2. **Game Structure**
   - **Format**: 3 periods × 5 questions = 15 questions per game
   - **Overtime**: Sudden death if tied after regulation
   - **Time Limit**: 30 seconds per question
   - **Progression**: Auto-advance after answer or timeout

3. **Scoring System**
   - **Correct Answer**: +1 goal for player
   - **Wrong Answer**: +1 goal for opponent
   - **Second Chance**: Half point (0.5 goals) if correct after hint
   - **Final Score**: Player Goals vs Opponent Goals

4. **Question Mechanics**
   - **Selection**: Random from category pools
   - **Types**: Multiple choice (4 options), True/False, Short answer
   - **AI Validation**: OpenAI checks short answers for correctness
   - **Hint System**: Socratic question on wrong answer for second attempt

5. **Leaderboard**
   - **Display**: Top 10 scores (nickname, score, date)
   - **Period**: Rolling 30-day window
   - **Privacy**: Nicknames only, no personal data

### Question Bank Categories
1. **Hockey Rules & Penalties** (20 questions)
   - Basic rules, offside, icing, penalties
2. **Team Systems** (20 questions)
   - Breakout plays, forechecking, power play from Notion site
   - Content pulled directly from team's Notion playbook pages
3. **NHL Knowledge** (15 questions)
   - Teams, famous players, Stanley Cup history
4. **Equipment & Safety** (10 questions)
   - Gear names, safety rules, proper fitting
5. **Sportsmanship** (10 questions)
   - Teamwork, respect, fair play concepts

### Content Guidelines
- **Reading Level**: Grade 4 (age 9-10)
- **Language**: Positive, encouraging, no complex jargon
- **Feedback**: Celebratory for correct, supportive for wrong
- **Examples**:
  - ✅ "Great goal! You're on fire!"
  - ✅ "Nice try! Here's a hint..."
  - ❌ No negative reinforcement

## 💻 Technical Requirements

### Architecture
```
Next.js App (Vercel)
├── Frontend (React + Tailwind)
├── API Routes
│   ├── /api/questions - Get random questions
│   ├── /api/validate - AI answer checking
│   └── /api/leaderboard - Score management
└── External Services
    ├── OpenAI API - Answer validation
    └── Vercel KV - Leaderboard storage
```

### Technology Stack
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Database**: Vercel KV (Redis)
- **AI Service**: OpenAI GPT-4o-mini
- **Deployment**: Vercel
- **Analytics**: Vercel Analytics (optional)

### Design System
- **Colors** (matching team Notion site):
  - Primary: Red (#DC2626)
  - Secondary: Black (#000000)
  - Accent: Grey (#6B7280)
  - Background: White (#FFFFFF)
- **Typography**: 
  - Headers: Bold, sans-serif
  - Body: Regular, good readability
- **Logo**: Thunder logo in header (https://tedreevehockey.com/wp-content/uploads/2018/12/Thunder-1.png)
- **Animations**: Smooth transitions, goal celebrations

### API Endpoints

#### GET /api/questions
```typescript
Response: {
  questions: Question[]  // 5 random questions
  period: number         // Current period (1-3)
}
```

#### POST /api/validate
```typescript
Request: {
  question: string
  answer: string
  isSecondAttempt: boolean
}
Response: {
  correct: boolean
  hint?: string
  explanation?: string
}
```

#### GET /api/leaderboard
```typescript
Response: {
  scores: Score[]  // Top 10
}
```

#### POST /api/leaderboard
```typescript
Request: {
  nickname: string
  playerGoals: number
  opponentGoals: number
}
```

### Environment Variables
```env
OPENAI_API_KEY=sk-...
KV_URL=redis://...
KV_REST_API_URL=https://...
KV_REST_API_TOKEN=...
```

### Notion Embedding Requirements
- **Method**: iframe embed in Notion page
- **Target Page**: Team Notion site dashboard or dedicated quiz page
- **Responsive**: 100% width, min-height 600px
- **Security**: Content Security Policy headers configured for Notion
- **Performance**: < 2s initial load
- **URL Structure**: https://thunder-quiz.vercel.app (or custom domain)

### Embedding Code Example
```html
<iframe src="https://thunder-quiz.vercel.app" 
        width="100%" 
        height="700" 
        frameborder="0"
        allowfullscreen>
</iframe>
```

### Performance Targets
- **Initial Load**: < 2 seconds
- **Question Load**: < 500ms
- **AI Response**: < 3 seconds
- **Lighthouse Score**: > 90

## 📋 Implementation Tasks

### Phase 1: Core Setup
- [ ] Initialize Next.js project with TypeScript
- [ ] Configure Tailwind with team colors
- [ ] Set up Vercel deployment
- [ ] Create basic layout components

### Phase 2: Game Logic
- [ ] Implement question selection algorithm
- [ ] Build game flow state management
- [ ] Create period/overtime logic
- [ ] Add timer functionality

### Phase 3: UI Components
- [ ] Design welcome/nickname screen
- [ ] Build question display component
- [ ] Create score display (hockey rink visual)
- [ ] Implement answer feedback animations

### Phase 4: AI Integration
- [ ] Set up OpenAI API connection
- [ ] Create answer validation logic
- [ ] Implement hint generation
- [ ] Add retry mechanism for API failures

### Phase 5: Data Management
- [ ] Create question bank JSON
- [ ] Extract team systems from Notion site
- [ ] Set up Vercel KV database
- [ ] Implement leaderboard CRUD
- [ ] Add data validation

### Phase 6: Polish & Testing
- [ ] Add goal celebration animations
- [ ] Implement sound effects (optional)
- [ ] Create loading states
- [ ] Test Notion embedding
- [ ] Mobile responsiveness testing

### Phase 7: Deployment
- [ ] Configure production environment
- [ ] Set up monitoring/analytics
- [ ] Create embed documentation for Notion
- [ ] Deploy to Vercel
- [ ] Add to team Notion site

## 🚀 Success Metrics
- **Engagement**: 80% of team tries quiz within first week
- **Completion**: 70% finish full game session
- **Retention**: 50% play multiple times per month
- **Learning**: Measurable improvement in team system knowledge
- **Technical**: Zero downtime, < 3s response times

## 📝 Future Enhancements
- Team tournaments with brackets
- Coach dashboard for progress tracking
- Custom question creation interface
- Achievement badges and rewards
- Practice mode for specific topics
- Parent progress reports
- Integration with team statistics from Notion