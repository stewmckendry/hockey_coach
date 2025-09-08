# Thunder Hockey Quiz App - Design Specification

## 🏒 Project Overview
Interactive hockey quiz application for U10A Ted Reeve Thunder team, designed to be embedded directly in their Notion team site for player engagement and learning.

**Team Notion Site**: https://www.notion.so/U10A-Ted-Reeves-Thunder-2660cdbf49778099a6bbccfc949f854b

## 📅 Implementation Status
**Last Updated**: December 8, 2024
**Current Status**: MVP Complete, Enhancements In Progress

### ✅ Completed Features
- Next.js app with TypeScript and Tailwind CSS
- Welcome screen with Thunder logo and nickname entry
- Game state management with React Context
- Question display with multiple choice, true/false, and short answer
- Score display with hockey rink visual
- 60-second timer per question (updated from 30s)
- OpenAI integration for answer validation
- Leaderboard with Vercel KV (fallback to local storage)
- 94 question bank across 9 categories with AI enrichment
- Responsive design with improved UI/UX

### ✅ Recent Enhancements
1. **Visual Design Updates** - COMPLETE
   - Match Notion site typography and spacing
   - Implement cleaner, more spacious layout
   - Use actual Thunder logo throughout

2. **Hint System Fix** - COMPLETE
   - Display hint longer for reading
   - Allow second attempt after hint
   - Track half-point scoring correctly

3. **Leaderboard Persistence** - COMPLETE
   - Fix score submission to persist properly
   - Ensure scores show after game completion

4. **Enhanced Question Bank** - COMPLETE
   - **Total Questions**: 94 (expanded from 55)
   - **AI-Powered Enrichment**: All questions analyzed and tagged with:
     - Difficulty ratings (easy/medium/hard)
     - Topic metadata for diversity
     - Age-appropriate validation
     - Reading time estimates
   - **Progressive Difficulty System**: 
     - Period 1: Easy questions
     - Period 2: Mix of medium and easy
     - Period 3: Hard and medium questions
   - **Topic Diversity Algorithm**: Ensures varied categories in each game

5. **Kid-Friendly UX Improvements** - COMPLETE
   - **Welcome Screen**:
     - Animated Thunder logo with bounce effect
     - Thunder mascot character integration
     - Gradient text effects with team colors
     - Ice rink pattern background
     - Interactive nickname field with lightning bolt feedback
     - Animated "How to Play" icons
     - Larger, more exciting Start Game button
   - **Question Display**:
     - Animated True/False buttons with ✅❌ emojis
     - Color-coded category badges with icons
     - Gradient backgrounds and scale animations
     - Enhanced padding on all interactive elements
   - **Improved Randomization**:
     - Fisher-Yates shuffle algorithm for true randomness
     - Better question distribution across difficulty levels
   - **Quality of Life**:
     - Enter key submits short answers
     - Fixed 2-on-1 defense question accuracy
     - More lenient answer validation for kids

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
   - **Time Limit**: ~~30~~ **60 seconds per question** (updated for kids)
   - **Progression**: Auto-advance after answer or timeout

3. **Scoring System**
   - **Correct Answer**: +1 goal for player
   - **Wrong Answer**: +1 goal for opponent
   - **Second Chance**: Half point (0.5 goals) if correct after hint
   - **Final Score**: Player Goals vs Opponent Goals

4. **Question Mechanics**
   - **Selection**: Progressive difficulty with topic diversity algorithm
     - Period 1: 5 easy questions from varied categories
     - Period 2: 3 medium + 2 easy questions with diversity
     - Period 3: 3 hard + 2 medium questions with diversity
   - **Types**: Multiple choice (4 options), True/False, Short answer
   - **AI Validation**: OpenAI GPT-4o-mini checks all answers
     - Direct comparison for MC/TF
     - Fuzzy matching for short answers
     - Generates contextual hints on wrong answers
   - **Hint System**: 
     - Shows helpful hint on wrong answer
     - Allows second attempt for half points
     - Hint stays visible for adequate reading time
   - **Question Enrichment**: LLM-powered metadata including:
     - Difficulty calibration for U10 players
     - Topic tagging for diversity tracking
     - Age-appropriate content validation

5. **Leaderboard**
   - **Display**: Top 10 scores (nickname, score, accuracy, date)
   - **Period**: Rolling 30-day window
   - **Privacy**: Nicknames only, no personal data
   - **Storage**: Primary Notion database, with Vercel KV/local fallback
   - **Notion Integration**: Scores saved to team's Notion workspace for coach/parent visibility

### Question Bank Categories (94 Total Questions)
1. **Hockey Rules & Penalties** (25 questions)
   - Basic rules, offside, icing, penalties
   - Advanced: double minors, match penalties, delayed penalties
2. **Team Systems** (22 questions)
   - Thunder-specific: 2-1-2 forecheck, breakouts, defensive positioning
   - Team values: Fast, Smart, Together
3. **NHL Knowledge** (12 questions)
   - Teams, famous players, Stanley Cup history
   - Trophies: Hart, Selke, Norris, Vezina
4. **Team Tactics** (11 questions)
   - Power play formations (1-3-1, umbrella)
   - Penalty kill systems (box, diamond, wedge)
   - Cycling, forechecking strategies
5. **Skills & Fundamentals** (11 questions)
   - Skating, passing, shooting techniques
   - Advanced moves: Michigan, Forsberg deke
6. **Equipment & Safety** (6 questions)
   - Gear names, safety rules, proper fitting
7. **Sportsmanship** (4 questions)
   - Teamwork, respect, fair play concepts
8. **Practice & Drills** (2 questions)
   - Training concepts, practice routines
9. **Fun Facts** (1 question)
   - Interesting hockey trivia

**Difficulty Distribution**:
- Easy: 15 questions (16%)
- Medium: 36 questions (38%)
- Hard: 43 questions (46%)

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
│   ├── /api/leaderboard - Local score management (fallback)
│   └── /api/notion-leaderboard - Primary Notion database
└── External Services
    ├── OpenAI API - Answer validation
    ├── Notion API - Primary leaderboard storage
    └── Vercel KV - Leaderboard fallback
```

### Technology Stack
- **Framework**: Next.js 15.5.2 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Database**: Vercel KV (Redis) with local fallback
- **AI Service**: OpenAI GPT-4o-mini
- **Deployment**: Vercel
- **Package Manager**: npm

### Design System (Updated)
- **Colors** (Thunder team colors):
  - Primary: Red (#DC2626)
  - Secondary: Black (#000000)
  - Accent: Grey (#6B7280)
  - Background: White (#FFFFFF)
  - Light Grey: (#F3F4F6)
- **Typography**: 
  - Font: Inter (matching Notion)
  - Headers: Bold, larger sizing
  - Body: Regular, enhanced readability
- **Logo**: Thunder logo integrated (downloaded locally)
- **Layout**:
  - Card-based design with rounded corners (rounded-xl)
  - Subtle shadows for depth
  - Gradient backgrounds for visual interest
  - Better spacing and padding throughout
- **Animations**: 
  - Goal celebrations
  - Smooth transitions
  - Hover effects on buttons
  - Timer color changes

### Component Structure
```
components/
├── game/
│   ├── WelcomeScreen.tsx    # Nickname entry with Thunder branding
│   ├── QuestionDisplay.tsx  # Question & answer interface
│   ├── ScoreDisplay.tsx     # Hockey rink score visual
│   ├── GameContainer.tsx    # Main game orchestrator
│   └── Leaderboard.tsx      # Top 10 scores display
lib/
├── gameContext.tsx           # React Context for state
└── types.ts                  # TypeScript definitions
```

### API Endpoints

#### POST /api/questions
Returns 15 random questions with balanced category distribution

#### POST /api/validate
- Uses OpenAI for intelligent answer validation
- Generates hints for wrong answers
- Supports fuzzy matching for short answers

#### GET/POST /api/leaderboard
- Retrieves top 10 scores (local/KV fallback)
- Submits new scores with ranking (fallback)

#### GET/POST /api/notion-leaderboard
- **Primary leaderboard system**
- Retrieves scores from team's Notion database
- Submits scores directly to Notion for coach/parent visibility
- Database ID: `2680cdbf-4977-8119-89fc-fba3dd92f096`

### Environment Variables
```env
OPENAI_API_KEY=sk-proj-...        # Configured from existing .env
NOTION_API_KEY=ntn_v345...        # For leaderboard integration
KV_URL=redis://...                # Auto-configured by Vercel (fallback)
KV_REST_API_URL=https://...       # Auto-configured by Vercel (fallback)
KV_REST_API_TOKEN=...             # Auto-configured by Vercel (fallback)
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Notion Embedding Requirements
- **Method**: iframe embed in Notion page
- **Target Page**: Team Notion site dashboard or dedicated quiz page
- **Responsive**: 100% width, min-height 700px
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

## 📋 Implementation Progress

### ✅ Phase 1: Core Setup - COMPLETE
- [x] Initialize Next.js project with TypeScript
- [x] Configure Tailwind with team colors
- [x] Set up local development environment
- [x] Create basic layout components

### ✅ Phase 2: Game Logic - COMPLETE
- [x] Implement question selection algorithm
- [x] Build game flow state management
- [x] Create period/overtime logic
- [x] Add timer functionality (60 seconds)

### ✅ Phase 3: UI Components - COMPLETE
- [x] Design welcome/nickname screen with Thunder logo
- [x] Build question display component
- [x] Create score display (hockey rink visual)
- [x] Implement answer feedback animations

### ✅ Phase 4: AI Integration - COMPLETE
- [x] Set up OpenAI API connection
- [x] Create answer validation logic
- [x] Implement hint generation
- [x] Add retry mechanism for API failures

### ✅ Phase 5: Data Management - COMPLETE
- [x] Create question bank JSON (94 questions with AI enrichment)
- [x] Implement LLM-powered question enrichment system
- [x] Add progressive difficulty selection algorithm
- [x] Create topic diversity algorithm for varied gameplay
- [x] Set up Vercel KV database config
- [x] Implement leaderboard CRUD (local/KV fallback)
- [x] Add Notion API integration for primary leaderboard
- [x] Add data validation
- [x] Create dual-storage system (Notion primary, local fallback)

### ✅ Phase 6: Polish & Testing - COMPLETE
- [x] Add goal celebration animations
- [x] Fix hint system for second attempts
- [x] Fix leaderboard persistence with Notion integration
- [x] Create loading states
- [x] Test Notion leaderboard API endpoints
- [ ] Test full Notion embedding
- [ ] Mobile responsiveness testing

### ⏳ Phase 7: Deployment - PENDING
- [ ] Configure production environment
- [ ] Set up monitoring/analytics
- [ ] Create embed documentation for Notion
- [ ] Deploy to Vercel
- [ ] Add to team Notion site

## 🐛 Known Issues & Fixes Needed
1. ✅ ~~**Hint System**: Need to allow second attempt after hint with proper timing~~ - FIXED
2. ✅ ~~**Leaderboard**: Scores not persisting properly after game~~ - FIXED with Notion integration
3. ✅ ~~**Visual Design**: Need to match Notion site typography/spacing~~ - IMPROVED
4. ✅ ~~**Question Bank**: Need to add team-specific content~~ - EXPANDED to 94 questions with AI enrichment

### Current Status
All major enhancements complete! App features:
- 94 diverse questions with progressive difficulty
- AI-powered question enrichment and metadata
- Topic diversity algorithm for varied gameplay
- Optimized for U10 hockey players (ages 9-10)
- Ready for deployment and Notion embedding

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
- Sound effects for goals and correct answers
- Seasonal themes and special events