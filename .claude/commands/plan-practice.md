---
description: "Create comprehensive hockey practice plans with drills, videos, and diagrams based on team context and coaching focus areas"
argument-hint: "<duration-minutes> <age-group> <focus-areas> [team-name]"
allowed-tools: ["mcp__notion-remote__search", "mcp__notion-remote__fetch", "mcp__notion-remote__create-pages", "mcp__notion-remote__update-page", "mcp__hockey-coaching__search_hockey_tactics", "mcp__hockey-coaching__search_hockey_videos", "mcp__hockey-coaching__search_hockey_drills", "mcp__hockey-coaching__search_hockey_skills", "mcp__hockey-coaching__search_hockey_dryland", "mcp__hockey-coaching__search_hockey_dryland_videos", "mcp__hockey-coaching__search_hockey_nhl_insights", "mcp__hockey-coaching__search_hockey_rules", "mcp__exa__web_search_exa", "mcp__youtube__videos_searchVideos", "mcp__youtube__videos_getVideo", "mcp__youtube__transcripts_getTranscript", "mcp__hockey-diagram__generate_hockey_diagram", "mcp__cloudinary__upload", "Read", "Grep", "TodoWrite"]
---

# Plan Practice Command

Creates comprehensive, age-appropriate hockey practice plans through intelligent orchestration of research, content generation, and visual creation tools. Designed for coaches who need quality practice plans quickly (2-3 times per week for 8-month seasons).

## Command Usage

```bash
# Basic usage
/plan-practice 60 U10 "passing, defensive positioning"

# With team context
/plan-practice 45 U12 "skating, breakouts" "Thunder Wolves"

# Multiple focus areas
/plan-practice 90 U14 "power play, penalty kill, faceoffs" "Lightning Elite"
```

## Workflow Implementation

### Phase 1: Parse Arguments and Initialize
1. **Extract Parameters:**
   - Duration (in minutes)
   - Age group (U8, U10, U12, U14, U16, U18)
   - Focus areas (comma-separated list)
   - Team name (optional)

2. **Create Todo List:**
   ```
   - [ ] Search for team context
   - [ ] Research drills for focus areas
   - [ ] Generate practice structure
   - [ ] Create visual content
   - [ ] Build Notion page
   - [ ] Add to Practice Plans database
   ```

3. **Load Guidelines:**
   - Read PRACTICE_GUIDELINES.md
   - Read PRACTICE_PLAN_TEMPLATE.md
   - Apply age-specific considerations

### Phase 2: Team Context Retrieval
**Search for Team Information:**
```
mcp__notion-remote__search
Query: "Team Information [team-name]"
```

**Extract Team Context:**
- Coaching philosophy
- Skill level
- Available equipment
- Recent practice history (if Practice Plans database exists)
- Season goals and focus areas

**Recent Practice Analysis (if available):**
```
mcp__notion-remote__search
Query: "Practice Plan [team-name] type:page"
Filter: Last 2 weeks
Extract: Focus areas, feedback, effectiveness ratings
```

### Phase 3: Hockey Knowledge Research

**Multi-Source Research for Each Focus Area:**

1. **Drill Research:**
   ```
   mcp__hockey-coaching__search_hockey_drills
   Query: "[age-group] [focus-area] drill"
   Results: 5-10 per focus area
   ```

2. **Skill Development Research:**
   ```
   mcp__hockey-coaching__search_hockey_skills
   Query: "[age-group] [focus-area] progression"
   Results: Age-appropriate progressions
   ```

3. **Tactical Concepts (if applicable):**
   ```
   mcp__hockey-coaching__search_hockey_tactics
   Query: "[focus-area] system [age-group]"
   Results: Team tactics and positioning
   ```

4. **Video Demonstrations:**
   ```
   mcp__hockey-coaching__search_hockey_videos
   Query: "[age-group] [focus-area] demonstration"
   Results: 3-5 quality videos
   ```

5. **External Web Research (Current Best Practices):**
   ```
   mcp__exa__web_search_exa
   Query: "hockey [focus-area] drills [age-group] coaching 2024"
   numResults: 5
   Purpose: Find latest coaching innovations and techniques
   ```

**Exa Research Benefits:**
- Current coaching trends and innovations
- New drill variations from professional coaches
- Safety updates and equipment recommendations
- Cross-training ideas from other sports
- Age-specific development research

### Phase 4: Practice Structure Generation

**Apply Time Allocations:**
```python
# Flexible allocation based on coach focus
if primary_focus_specified:
    allocations = adjust_for_focus(duration, primary_focus)
else:
    allocations = standard_allocations(duration)

# Account for realistic factors
actual_ice_time = duration - 5  # Getting on ice
add_transition_time(2 * num_activities)
add_water_breaks(ceil(duration / 30) * 2)
```

**Structure Components:**
1. **Warm-up** - Fun, engaging, movement-based (includes name games for first practice)
2. **Skill Stations** - Focus area drills with demonstrations
3. **Team Concepts** - Systems work (if age-appropriate)  
4. **Game Simulation** - Applied skills
5. **Cool-down** - Positive ending (team building for first practice)
6. **Water/Transitions** - Built into time allocations (3-4 minutes per break)

**Visual Content Requirements:**
- U8: 80% visual content (diagrams, demos, videos)
- U10: 70% visual content
- U12: 60% visual content
- U14+: 50% visual content

**Drill Selection Criteria:**
- High repetition rate
- Age-appropriate complexity
- Relates to focus areas  
- Progressive difficulty options
- Safety considerations
- Coach assignments specified

### Phase 5: Visual Content Generation

**For Each Key Drill:**

1. **Generate Tactical Diagram:**
   ```
   mcp__hockey-diagram__generate_hockey_diagram
   Prompt: "[drill-name] setup with [player-count] players [specific-details]"
   ```

2. **Upload to Cloudinary:**
   ```
   mcp__cloudinary__upload
   File: [generated-diagram]
   Folder: "hockey-coaching/practice-plans/[date]"
   ```

3. **Search for Video Demonstrations:**
   ```
   mcp__youtube__videos_searchVideos
   Query: "[drill-name] hockey coaching [age-group]"
   maxResults: 3
   ```

4. **Quality Validation:**
   - Check video duration (appropriate for age)
   - Verify channel credibility
   - Extract key timestamps if available
   
5. **Diagram Fallback (if generation unavailable):**
   ```
   [DIAGRAM PLACEHOLDER: Drill Name]
   - Player positions and movements
   - Cone/obstacle placement  
   - Traffic flow patterns
   ```

### Phase 6: Practice Plan Assembly

**Create Structured Content Following Template:**
```markdown
# Practice Plan: [Team Name] - [Date]

## Practice Overview
- Duration: [X] minutes
- Focus Areas: [Primary], [Secondary]
- Age Group: [UXX]
- Players Expected: [From team info or estimate]

## Equipment Needed
- [ ] Pucks (50+) in buckets
- [ ] Cones (20+ various colors)
- [ ] Small nets/targets (4-6)
- [ ] Pylons (8-10)  
- [ ] Tires/obstacles (4-6)
- [ ] Whiteboard & markers
- [ ] Clipboards (1 per coach)
- [ ] First aid kit at bench
- [ ] Extra water bottles
[Additional equipment specific to drills]

## Coach Assignments
- Head Coach: [Main instruction, team concepts]
- Assistant 1: [Station 1, skill development]
- Assistant 2: [Station 2, small games]
- Parent Helper: [Equipment, water, encouragement]

## Practice Flow

### Warm-up ([X] minutes)
[Selected warm-up activity with diagram]

### Skill Development ([X] minutes)
#### Station 1: [Focus Area]
[Drill with diagram, coaching points, variations]

#### Station 2: [Focus Area]
[Drill with diagram, coaching points, variations]

### Team Concepts ([X] minutes)
[System work with tactical diagram]

### Game Simulation ([X] minutes)
[Scrimmage format with focus points]

### Cool-down ([X] minutes)
[Fun activity to end practice]
**First Practice Special:**
- Create team cheer together
- Team handshake or fist bump line  
- Group photo opportunity
- Announce next practice details

## Contingency Plans
### Group Size Variations & Time Adjustments
[Specific adaptations for different scenarios]

## Coaching Reminders
[Age-specific tips from guidelines]

## Videos & Resources
[Embedded YouTube videos with descriptions]
```

### Phase 7: Notion Page Creation

**Create Practice Plan Page:**
```
mcp__notion-remote__create-pages
Parent: Team workspace or general area
Title: "Practice Plan - [Date] - [Focus]"
Content: [Assembled practice plan with embedded media]
```

**Add to Practice Plans Database:**
```
mcp__notion-remote__update-database
Database: Practice Plans
Properties:
  - Title: "Practice - [Date] - [Focus]"
  - Date: [Practice date]
  - Duration: [Minutes]
  - Focus Areas: [Multi-select values]
  - Age Group: [Select value]
  - Practice Rating: [Empty - for post-practice]
  - Post-Practice Feedback: [Empty - for post-practice]
```

### Phase 8: Delivery and Iteration

**Present to Coach:**
```
✅ Practice Plan Created!

📋 Notion Page: [Link to practice plan]

Summary:
- Duration: [X] minutes
- Focus: [Primary areas]
- Stations: [Number] skill development stations
- Videos: [Number] demonstration videos included
- Diagrams: [Number] tactical diagrams generated

Key Elements:
1. [Highlight 1]
2. [Highlight 2]
3. [Highlight 3]

Questions to Consider:
- Does the skill progression match your team's current level?
- Would you like more emphasis on any particular area?
- Should we adjust the scrimmage format?

Reply with any changes you'd like, or say "good to go" to finalize.
```

**Handle Feedback:**
If coach requests changes:
```
mcp__notion-remote__update-page
Page: [Practice plan URL]
Updates: [Specific modifications requested]
```

## Error Handling

### Team Not Found
```
Team '[team-name]' not found in Team Information database.

Creating general [age-group] practice plan.
To enable team-specific plans, first run:
/setup-team '[team-name]' [age-group]

Continuing with practice plan generation...
```

### Invalid Age Group
```
Invalid age group '[input]'.
Valid age groups: U8, U10, U12, U14, U16, U18

Please specify a valid age group.
```

### MCP Tool Failures
```
If hockey-coaching MCP unavailable:
  "Hockey MCP tools unavailable. Using alternative sources..."
  - Fallback to Exa web search for drills
  - Use YouTube for video content
  - Apply general practice structure from guidelines

If Exa search unavailable:
  "Web search unavailable. Using local knowledge base only..."
  - Continue with hockey MCP tools
  - Focus on proven drill database

If Notion creation fails:
  "Unable to create Notion page. Here's your practice plan:"
  [Display full practice plan in chat]
  "You can copy this to Notion manually."

If diagram generation fails:
  "Unable to generate tactical diagrams."
  "Using text descriptions for drill setup."
```

## Research Integration Examples

### Combining Multiple Sources
```
For "passing drills U10":

1. Hockey MCP Results:
   - Basic stationary passing
   - Partner passing progression
   - Triangle passing drill

2. Exa Web Search Results:
   - "Small area passing games trending in 2024"
   - "European passing techniques for youth"
   - "Fun passing competitions for U10"

3. Combined Output:
   - Traditional drills + innovative variations
   - Safety updates from recent research
   - Engagement techniques from current trends
```

## Optimizations for Regular Use

### Quick Mode (for experienced coaches)
- Skip detailed explanations
- Use previous practice feedback
- Minimal coach interaction needed
- Auto-apply successful patterns

### Template Matching
- Identify common request patterns
- Pre-select appropriate drills
- Faster generation for repeat focuses

### Feedback Learning
- Search for highly-rated similar practices
- Avoid previously marked ineffective drills
- Build on successful elements

## Integration Features

### Season Planning Connection
- Reference monthly themes
- Progressive skill building
- Preparation for upcoming games

### Multi-Team Support
- Separate practice histories
- Team-specific adaptations
- Shared drill library

### Analytics Integration
- Track focus area distribution
- Monitor drill effectiveness
- Identify improvement areas

## Quality Assurance

### Pre-Delivery Checklist
- ✓ Age-appropriate content
- ✓ Safety considerations included
- ✓ Time allocations realistic
- ✓ Diagrams clear and accurate
- ✓ Videos quality validated
- ✓ Progressive difficulty options
- ✓ Fun elements included

### Post-Practice Integration
Coach can update practice plan with:
- Effectiveness rating
- What worked/didn't work
- Player engagement level
- Notes for next practice

This feedback improves future practice plans through searchable history.

## Example Executions

### Example 1: Basic Practice
```bash
/plan-practice 60 U10 "passing, shooting"

Output:
"Creating 60-minute U10 practice plan focused on passing and shooting...

🔍 Researching age-appropriate drills...
📊 Found 12 passing drills and 8 shooting drills
🌐 Discovered 3 innovative passing games from recent coaching articles
🎥 Located 5 demonstration videos
🎨 Generating 4 tactical diagrams...

✅ Practice plan created!"
[Notion link]
```

### Example 2: Team-Specific Practice
```bash
/plan-practice 45 U12 "defensive zone coverage" "Thunder Hawks"

Output:
"Creating 45-minute practice for Thunder Hawks U12...

👥 Found team context: Competitive level, working on systems
📚 Recent practices focused on offensive play
🌐 Researching latest defensive zone tactics for U12...
🎯 Adjusting to emphasize defensive systems...

✅ Practice plan created with team-specific adaptations!"
[Notion link]
```

### Example 3: Extended Practice
```bash
/plan-practice 90 U16 "conditioning, special teams, scrimmage"

Output:
"Creating 90-minute U16 practice with multiple focus areas...

⚡ High-intensity practice planned
🌐 Found new conditioning drills from pro training methods
🏃 Conditioning integrated throughout
📋 Power play and penalty kill systems included
🏒 Extended scrimmage time allocated

✅ Comprehensive practice plan created!"
[Notion link]
```

## Success Metrics

1. **Generation Time**: < 5 minutes from request to delivery
2. **Completeness**: All sections populated with relevant content
3. **Visual Content**: Minimum 2-3 diagrams, 2-3 videos
4. **Customization**: Team context reflected when available
5. **Iteration Rate**: < 2 rounds of feedback needed
6. **Usage Frequency**: Supports 2-3 practices per week efficiently

This command streamlines the entire practice planning process while maintaining quality and customization, perfect for busy coaches who need effective practices quickly.