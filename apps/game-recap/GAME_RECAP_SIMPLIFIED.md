# 🏒 Simplified Game Recap System
*Airtable → n8n → AI → Notion Pipeline*

## Overview
Simple automated pipeline that transforms game stats into kid-friendly story recaps. Manual trigger via n8n browser, no UI needed.

---

## 📊 Airtable Setup

### Single Table: `game_stats` (in thunder_hockey base)

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| game_id | Autonumber | Unique identifier | 1 |
| date | Date | Game date | 2025-01-10 |
| opponent | Single line text | Opposing team | Eagles |
| location | Single select | Home/Away | Home |
| our_score | Number | Our final score | 5 |
| their_score | Number | Opponent score | 3 |
| game_type | Single select | Regular/Tournament/Playoff | Regular |
| player_goals | Long text | Goals by player (JSON) | {"Jamie": 2, "Sam": 1, "Alex": 2} |
| player_assists | Long text | Assists by player (JSON) | {"Pat": 3, "Jordan": 2} |
| goalie_saves | Number | Total saves by goalie | 28 |
| shots_on_goal | Number | Our shots on goal | 32 |
| penalty_minutes | Number | Our penalty minutes | 6 |
| power_play_goals | Number | PP goals scored | 2 |
| special_moments | Long text | Notable plays/events | "Jamie hat trick, Alex amazing glove save in 3rd" |
| processed | Checkbox | Workflow completed | ☐ |
| recap_url | URL | Link to Notion page | https://notion.so/... |

---

## 🎮 Test Data (5 Sample Games)

### Game 1: Big Win
```json
{
  "date": "2025-01-08",
  "opponent": "Eagles",
  "location": "Home",
  "our_score": 7,
  "their_score": 2,
  "game_type": "Regular",
  "player_goals": "{\"Jamie\": 3, \"Sam\": 2, \"Alex\": 1, \"Jordan\": 1}",
  "player_assists": "{\"Pat\": 4, \"Casey\": 2, \"Morgan\": 2}",
  "goalie_saves": 18,
  "shots_on_goal": 42,
  "penalty_minutes": 4,
  "power_play_goals": 2,
  "special_moments": "Jamie hat trick! Sam scored from center ice. Team played amazing passing game."
}
```

### Game 2: Close Loss
```json
{
  "date": "2025-01-06",
  "opponent": "Hawks",
  "location": "Away",
  "our_score": 3,
  "their_score": 4,
  "game_type": "Regular",
  "player_goals": "{\"Alex\": 1, \"Jordan\": 1, \"Pat\": 1}",
  "player_assists": "{\"Jamie\": 2, \"Sam\": 1}",
  "goalie_saves": 35,
  "shots_on_goal": 28,
  "penalty_minutes": 8,
  "power_play_goals": 1,
  "special_moments": "Riley made 35 saves! Fought hard until final buzzer. Great team effort despite loss."
}
```

### Game 3: Comeback Victory
```json
{
  "date": "2025-01-03",
  "opponent": "Lightning",
  "location": "Home",
  "our_score": 5,
  "their_score": 4,
  "game_type": "Tournament",
  "player_goals": "{\"Casey\": 2, \"Morgan\": 2, \"Sam\": 1}",
  "player_assists": "{\"Alex\": 3, \"Jamie\": 2}",
  "goalie_saves": 29,
  "shots_on_goal": 35,
  "penalty_minutes": 6,
  "power_play_goals": 1,
  "special_moments": "Down 4-2 entering third period. Casey scored twice in final 5 minutes for the win!"
}
```

### Game 4: Defensive Battle
```json
{
  "date": "2024-12-28",
  "opponent": "Bears",
  "location": "Away",
  "our_score": 2,
  "their_score": 1,
  "game_type": "Regular",
  "player_goals": "{\"Jordan\": 1, \"Pat\": 1}",
  "player_assists": "{\"Morgan\": 1, \"Casey\": 1}",
  "goalie_saves": 38,
  "shots_on_goal": 22,
  "penalty_minutes": 2,
  "power_play_goals": 0,
  "special_moments": "Riley stood on their head with 38 saves! Defense blocked 15 shots. Total team defense!"
}
```

### Game 5: Tournament Championship
```json
{
  "date": "2024-12-22",
  "opponent": "Sharks",
  "location": "Neutral",
  "our_score": 4,
  "their_score": 3,
  "game_type": "Playoff",
  "player_goals": "{\"Jamie\": 1, \"Sam\": 1, \"Alex\": 1, \"Jordan\": 1}",
  "player_assists": "{\"Pat\": 2, \"Casey\": 1, \"Morgan\": 1}",
  "goalie_saves": 31,
  "shots_on_goal": 37,
  "penalty_minutes": 4,
  "power_play_goals": 1,
  "special_moments": "Championship game! Jordan scored game winner with 45 seconds left. First tournament win of season!"
}
```

---

## 🔧 n8n Workflow Design

### Workflow Name: `Thunder_Game_Recap_Generator`

### Node Configuration

#### 1. Manual Trigger
- **Type**: Manual Trigger
- **Purpose**: Start workflow on demand from n8n UI

#### 2. Airtable - Get Unprocessed Games
- **Operation**: List
- **Base ID**: `[thunder_hockey base ID]`
- **Table**: `game_stats`
- **Filter**: `AND({processed} = FALSE(), {date} != "")`
- **Sort**: Date (Ascending)
- **Limit**: 5

#### 3. Loop Over Games
- **Type**: Split In Batches
- **Batch Size**: 1
- **Purpose**: Process each game individually

#### 4. Format Game Data
- **Type**: Code Node
```javascript
const gameData = $input.first().json;

// Parse JSON strings
const goals = JSON.parse(gameData.player_goals || "{}");
const assists = JSON.parse(gameData.player_assists || "{}");

// Format for AI
return {
  json: {
    game_summary: {
      date: gameData.date,
      opponent: gameData.opponent,
      location: gameData.location,
      final_score: `Thunder ${gameData.our_score} - ${gameData.opponent} ${gameData.their_score}`,
      result: gameData.our_score > gameData.their_score ? "WIN" : "LOSS",
      game_type: gameData.game_type
    },
    statistics: {
      goals_by_player: goals,
      assists_by_player: assists,
      goalie_saves: gameData.goalie_saves,
      shots_on_goal: gameData.shots_on_goal,
      power_play_goals: gameData.power_play_goals,
      penalty_minutes: gameData.penalty_minutes
    },
    highlights: gameData.special_moments,
    game_id: gameData.game_id
  }
};
```

#### 5. Generate AI Recap
- **Type**: OpenAI / HTTP Request to Claude
- **Model**: GPT-4 or Claude 3
- **Prompt**:
```
You are a youth hockey team storyteller creating fun recaps for kids aged 8-14 and their families.

Game Data:
{{$json.game_summary}}

Statistics:
{{$json.statistics}}

Special Moments:
{{$json.highlights}}

Create an engaging game recap with:

1. HEADLINE (8-10 words, exciting and catchy)

2. THE STORY (150-200 words)
- Write in an enthusiastic, positive tone
- Mention specific players by name (use only first names)
- Celebrate both individual achievements and team effort
- If it was a loss, focus on positives and fighting spirit
- Include one "Did you know?" fact

3. THREE STARS
- First Star: [Player] - [Why they earned it]
- Second Star: [Player] - [Why they earned it]  
- Third Star: [Player] - [Why they earned it]

4. COACH'S CORNER
- One key learning moment or team achievement (2 sentences)

Format as markdown. Be creative, fun, and always encouraging!
```

#### 6. Create Notion Page
- **Type**: Notion - Create Page
- **Parent Page**: `[Team Season Page ID]`
- **Title**: `{{$json.headline}}`
- **Content**:
```markdown
# {{$json.headline}}

📅 {{formatDate($json.game_summary.date, "MMMM D, YYYY")}}
🏒 vs {{$json.game_summary.opponent}} ({{$json.game_summary.location}})
🥅 Final Score: {{$json.game_summary.final_score}}

---

## 📖 The Story

{{$json.story}}

---

## ⭐ Three Stars of the Game

{{$json.three_stars}}

---

## 🎯 Coach's Corner

{{$json.coaches_corner}}

---

## 📊 Game Stats

- **Shots on Goal**: {{$json.statistics.shots_on_goal}}
- **Goalie Saves**: {{$json.statistics.goalie_saves}} 
- **Power Play Goals**: {{$json.statistics.power_play_goals}}
- **Penalty Minutes**: {{$json.statistics.penalty_minutes}}

---

*Generated by Thunder Game Recap System*
```

#### 7. Update Airtable Record
- **Operation**: Update
- **Record ID**: `{{$node["Loop Over Games"].json.id}}`
- **Fields**:
  - `processed`: true
  - `recap_url`: `{{$node["Create Notion Page"].json.url}}`

#### 8. Error Handler
- **Type**: Error Trigger
- **Connected to**: Slack/Email notification
- **Message**: "Failed to process game {{game_id}}: {{error.message}}"

---

## 🧪 Testing Plan

### Phase 1: Component Testing
1. ✅ Verify Airtable connection and data retrieval
2. ✅ Test JSON parsing in Code node
3. ✅ Validate AI prompt with single game
4. ✅ Confirm Notion page creation

### Phase 2: Integration Testing
1. Process single test game end-to-end
2. Verify Notion page formatting
3. Check Airtable update (processed flag)
4. Test error handling with bad data

### Phase 3: Batch Testing
1. Run workflow with all 5 test games
2. Verify loop processing
3. Check all Notion pages created
4. Confirm no duplicate processing

### Success Criteria
- [ ] All 5 test games generate unique recaps
- [ ] Recaps are age-appropriate and positive
- [ ] Player names appear correctly
- [ ] Notion pages are properly formatted
- [ ] Airtable records marked as processed
- [ ] No errors in workflow execution

---

## 🚀 Quick Start Commands

### 1. Create Airtable Table
```javascript
// Airtable API call to create table
{
  "name": "game_stats",
  "fields": [
    {"name": "date", "type": "date"},
    {"name": "opponent", "type": "singleLineText"},
    {"name": "location", "type": "singleSelect", "options": {"choices": [
      {"name": "Home"}, {"name": "Away"}, {"name": "Neutral"}
    ]}},
    {"name": "our_score", "type": "number"},
    {"name": "their_score", "type": "number"},
    {"name": "game_type", "type": "singleSelect", "options": {"choices": [
      {"name": "Regular"}, {"name": "Tournament"}, {"name": "Playoff"}
    ]}},
    {"name": "player_goals", "type": "multilineText"},
    {"name": "player_assists", "type": "multilineText"},
    {"name": "goalie_saves", "type": "number"},
    {"name": "shots_on_goal", "type": "number"},
    {"name": "penalty_minutes", "type": "number"},
    {"name": "power_play_goals", "type": "number"},
    {"name": "special_moments", "type": "multilineText"},
    {"name": "processed", "type": "checkbox"},
    {"name": "recap_url", "type": "url"}
  ]
}
```

### 2. n8n Workflow JSON (Import Template)
```json
{
  "name": "Thunder_Game_Recap_Generator",
  "nodes": [
    {
      "parameters": {},
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [250, 300]
    }
  ],
  "connections": {}
}
```

---

## 📝 Notes

- No UI needed - workflow runs from n8n browser interface
- Results viewable directly in Notion
- Can process multiple games in single run
- Easily extendable for season summaries
- Cost: ~$0.10 per game for AI generation

---

*Last Updated: January 2025*