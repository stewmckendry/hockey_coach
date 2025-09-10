# 🏒 Kid-Friendly Hockey Game Recap App
*Turning Stats into Stories for Young Hockey Fans*

## 📋 Executive Summary

An automated system that transforms game statistics into engaging, age-appropriate "headliner" recaps for youth hockey teams. The app uses n8n workflows to pull stats from Airtable, generate creative narratives with AI, and publish to the team's Notion site.

---

## 👥 User Journey

### Primary Users
- **Team Managers**: Upload game stats, review generated content
- **Parents**: Read recaps, share with family
- **Young Players (8-14)**: Enjoy fun stories about their games
- **Coaches**: Use recaps for team morale and teaching moments

### User Flow

```
1. POST-GAME (Team Manager)
   ↓ Enter stats in Airtable mobile app
   
2. AUTOMATED PROCESSING (n8n)
   ↓ Workflow triggers on new game entry
   ↓ AI generates multiple recap variations
   
3. REVIEW & PUBLISH (Team Manager)
   ↓ Quick approval in n8n dashboard
   ↓ Auto-publishes to Notion
   
4. CONSUMPTION (Team & Families)
   ↓ Read on Notion team page
   ↓ Share via social media
   ↓ Print for team bulletin board
```

---

## ⭐ Core Features

### 1. Smart Stat Input
- **Mobile-First Airtable Forms**
  - Quick entry templates for common stats
  - Player roster pre-populated
  - Game context fields (opponent, location, tournament)
  - Special moments tracker (first goal, great saves, teamwork)

### 2. AI-Powered Recap Generation
- **Multiple Narrative Styles**
  - "Sports Center" style headlines
  - Comic book adventure format
  - Player spotlight stories
  - Team achievement focus
  
- **Age-Appropriate Language**
  - Vocabulary suited for 8-14 year olds
  - Positive, encouraging tone
  - Emphasis on effort over outcome
  - Celebrating all contributions

### 3. Visual Enhancement
- **Auto-Generated Elements**
  - "Star of the Game" badges
  - Team achievement graphics
  - Fun stats infographics
  - Player quote bubbles

### 4. Publishing & Distribution
- **Notion Integration**
  - Automatic page creation
  - Organized by date/tournament
  - Player stats aggregation
  - Season storyline tracking

---

## 🛠 Technical Specification

### Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Airtable   │────▶│     n8n     │────▶│   Notion    │
│ (Game Stats)│     │  (Workflow) │     │ (Team Site) │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   OpenAI/   │
                    │   Claude    │
                    └─────────────┘
```

### Airtable Schema

#### Games Table
```
- game_id (autonumber)
- date (date)
- opponent (text)
- location (single select: Home/Away)
- final_score_us (number)
- final_score_them (number)
- game_type (single select: Regular/Tournament/Playoff)
- special_notes (long text)
```

#### Player Stats Table
```
- stat_id (autonumber)
- game_id (link to Games)
- player_name (link to Players)
- goals (number)
- assists (number)
- saves (number)
- great_plays (long text)
- attitude_award (checkbox)
```

#### Players Table
```
- player_id (autonumber)
- name (text)
- number (number)
- position (single select)
- nickname (text)
- fun_fact (text)
```

### n8n Workflow Components

#### 1. Trigger Node
- **Type**: Webhook / Schedule
- **Config**: 
  - Webhook for instant processing
  - Schedule for batch processing (every 30 min)

#### 2. Airtable Data Fetch
- **Nodes**:
  - Get new games (filterByFormula: "processed = FALSE()")
  - Get player stats for game
  - Get player details

#### 3. Data Transformation
- **Process**:
  - Merge game and player data
  - Calculate team totals
  - Identify standout performances
  - Format for AI prompt

#### 4. AI Recap Generation
- **OpenAI/Claude Node**:
```javascript
{
  "prompt": `
    Create a fun, kid-friendly hockey game recap:
    
    Game: {{gameData}}
    Player Stats: {{playerStats}}
    
    Requirements:
    - 3 paragraph story (150-200 words)
    - Include "Headline" (catchy 8-10 words)
    - Mention 3-4 specific players
    - Focus on effort and teamwork
    - Age-appropriate (8-14 years)
    - Positive tone even if lost
    - Include one "fun fact" or "did you know"
    
    Style: {{style}} (rotating: SportsCaster/Adventure/Comic)
  `,
  "temperature": 0.8,
  "max_tokens": 500
}
```

#### 5. Content Enhancement
- **Add Visual Elements**:
  - Generate emoji sequences for key moments
  - Create stat cards markdown
  - Format player quotes

#### 6. Notion Publishing
- **Create Page Node**:
  - Parent: Team Season Page
  - Title: Game headline
  - Properties: Date, Opponent, Score
  - Content: Full recap with formatting

#### 7. Notification & Logging
- **Success Path**:
  - Update Airtable (processed = TRUE)
  - Send Slack/Email notification
  - Log to monitoring

- **Error Handling**:
  - Retry logic (3 attempts)
  - Fallback to simple template
  - Alert team manager

### Notion Page Template

```markdown
# [HEADLINE]
*[Date] vs [Opponent]*

## 🏒 The Story
[AI Generated Recap]

## ⭐ Game Stars
- **Offensive Star**: [Player] - [Stats]
- **Defensive Star**: [Player] - [Achievement]
- **Hustle Award**: [Player] - [Effort noted]

## 📊 By The Numbers
- Goals: [Our goals] - [Their goals]
- Shots: [Total shots]
- Saves: [Goalie saves] ([Save %])
- Power Play: [PP goals]/[PP opportunities]

## 💬 Quote of the Game
> "[Generated or actual quote]" - [Player/Coach]

## 🎯 Team Achievements
- [Achievement 1]
- [Achievement 2]
- [Achievement 3]

---
*Generated with Thunder Playbook Game Recap System*
```

---

## 🚀 Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Set up Airtable base with schema
- [ ] Create sample data for 5 games
- [ ] Basic n8n workflow scaffold
- [ ] Simple AI prompt testing

### Phase 2: Core Workflow (Week 2)
- [ ] Complete n8n workflow implementation
- [ ] AI prompt refinement
- [ ] Error handling logic
- [ ] Basic Notion integration

### Phase 3: Enhancement (Week 3)
- [ ] Visual element generation
- [ ] Multiple style variations
- [ ] Parent notification system
- [ ] Performance optimization

### Phase 4: Testing & Launch (Week 4)
- [ ] Full system testing with real data
- [ ] Team manager training
- [ ] Documentation creation
- [ ] Production deployment

---

## 📊 Success Metrics

### Quantitative
- Recap generation time < 2 minutes
- 90%+ successful auto-generation rate
- Zero inappropriate content incidents
- 80%+ parent engagement rate

### Qualitative
- Kids excited to read recaps
- Parents sharing stories
- Coaches using for team building
- Positive team culture reinforcement

---

## 🔒 Safety & Moderation

### Content Guidelines
- No negative player comparisons
- Equal celebration of all positions
- Focus on improvement over criticism
- Respectful opponent mentions

### Technical Safeguards
- AI temperature limits (0.7-0.8)
- Content filtering keywords
- Manager approval step available
- Version history in Notion

---

## 💰 Cost Estimation

### Monthly Operational Costs
- **Airtable**: Free tier (sufficient for team)
- **n8n**: Self-hosted (free) or Cloud ($20/month)
- **OpenAI API**: ~$5/month (assuming 50 games)
- **Notion**: Free tier (sufficient)

**Total**: $0-25/month depending on hosting choice

---

## 🎯 Future Enhancements

### Version 2.0 Ideas
- Season-long narrative tracking
- Player achievement badges
- Parent mobile app
- Video highlight integration
- Multi-language support
- Tournament bracket tracking
- Practice recap generation
- Player-generated content sections

### Integration Opportunities
- Team photo integration
- Schedule sync
- Standings automation
- Social media auto-posting
- Email newsletter generation
- Team store merchandise ideas

---

## 📚 Appendix

### Sample Generated Recaps

#### SportsCaster Style
> **"Thunder Strike Twice in Third Period Comeback!"**
> 
> The Thunder showed true grit Saturday night, storming back from a 2-0 deficit to defeat the Eagles 3-2. Captain Jamie lit the lamp twice in the third period, while goalie Alex stood tall with 28 saves. The turning point came when the Thunder's power play unit, led by Sam's crisp passing, finally broke through. Did you know? This was the team's first comeback win of the season, proving that Thunder never gives up!

#### Adventure Style
> **"Quest for Victory: Thunder Heroes Emerge!"**
> 
> In the ice fortress of Hometown Arena, our brave Thunder warriors faced the mighty Eagles clan. Though the battle seemed lost, heroes emerged when needed most. Jamie the Swift struck with lightning speed, Sam the Wise set up the perfect play, and Alex the Guardian protected our net with incredible saves. Together, they completed their quest with a legendary 3-2 victory!

### Prompt Engineering Tips
1. Always include specific player names
2. Use active voice and vivid verbs
3. Balance individual and team achievements
4. Include a learning moment or fun fact
5. End on an uplifting note

### Troubleshooting Guide
- **Issue**: Recaps too generic
  - **Solution**: Add more specific stats and context to prompts

- **Issue**: Inappropriate language
  - **Solution**: Adjust temperature, add content filters

- **Issue**: Notion sync failures
  - **Solution**: Check API limits, implement retry logic

---

*Last Updated: January 2025*
*Version: 1.0*