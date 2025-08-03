# Practice Plan Architecture

## Overview

This document outlines a conversational AI-powered practice planning system that leverages Claude Code's existing MCP tools and native capabilities to create comprehensive, age-appropriate hockey practice plans through natural dialogue.

## Core Principle: Leverage Existing Tools, Not Build New Ones

Instead of building custom code, this architecture uses:
- **Native Claude Code conversation** for natural language understanding
- **MCP Tools** for all integrations (Notion, hockey-coaching, YouTube, hockey-diagram)
- **Markdown files** for guidelines and templates
- **Subagents** for complex multi-step operations

## User Flow Implementation

### 1. Natural Language Request
**User says:** "I need a practice plan for tomorrow's U10 practice. 60 minutes, focus on passing and defensive positioning."

**Claude Code:**
- Parses the natural language request
- Identifies: duration (60 min), age group (U10), focus areas (passing, defensive positioning)
- No slash command needed - just conversation

### 2. Team Context Retrieval
**Claude Code uses:**
```
mcp__notion-remote__search
- Query: "Team Information [team name from context or ask user]"
- Retrieves: age level, skill level, coaching philosophy, available equipment
```

**Stretch Goal:** Also search for previous practice plans:
```
mcp__notion-remote__search  
- Query: "Practice Plan [team name] type:page"
- Retrieves: recent practice history, coach feedback
```

### 3. Hockey Knowledge Research
**Claude Code orchestrates multiple MCP searches:**
```
mcp__hockey-coaching__search_hockey_drills
- Query: "U10 passing drills defensive positioning"
- Returns: age-appropriate drills with descriptions

mcp__hockey-coaching__search_hockey_skills
- Query: "U10 passing progression defensive skills"
- Returns: skill development pathways

mcp__hockey-coaching__search_hockey_tactics
- Query: "U10 defensive positioning systems"
- Returns: age-appropriate tactical concepts

mcp__hockey-coaching__search_hockey_videos
- Query: "U10 passing drills defensive positioning demonstration"
- Returns: curated instructional videos
```

### 4. Consult Practice Guidelines
**Claude Code reads:**
- `PRACTICE_GUIDELINES.md` - Best practices for practice structure
- `PRACTICE_PLAN_TEMPLATE.md` - Formatting template

### 5. Generate Practice Plan
**Claude Code creates structured plan:**
- Follows time allocations from guidelines
- Selects appropriate drills from research
- Includes variations and progressions
- Adds coaching points and safety reminders

### 6. Add Visual Content
**Claude Code generates visuals:**
```
mcp__hockey-diagram__generate_hockey_diagram
- For each drill needing visualization
- Creates tactical diagrams

mcp__youtube__search_videos
- Finds demonstration videos
- Gets relevant timestamps

mcp__cloudinary__upload
- Uploads generated diagrams
- Returns public URLs for embedding
```

### 7. Create in Notion
**Claude Code creates practice plan:**
```
mcp__notion-remote__create-pages
- Creates new page with practice plan
- Formats according to template
- Embeds images and videos
- Links to team page
```

**Stretch Goal:** Add to practice database:
```
mcp__notion-remote__update-database
- Add entry to Practice Plans database
- Include metadata: date, focus, duration
```

### 8. Share with Coach
**Claude Code presents:**
- Notion page link
- Practice summary in chat
- Key coaching points
- Questions for consideration

### 9. Iterative Refinement
**Coach provides feedback**
**Claude Code:**
```
mcp__notion-remote__update-page
- Updates the practice plan based on feedback
- Adjusts drills, timing, or focus
- Re-shares updated plan
```

## Implementation Strategy

### Phase 1: Core Documentation (Immediate)
1. Create `PRACTICE_GUIDELINES.md`
2. Create `PRACTICE_PLAN_TEMPLATE.md`
3. Document workflow in CLAUDE.md

### Phase 2: Workflow Testing (Next)
1. Test natural conversation flow
2. Validate MCP tool orchestration
3. Refine prompting patterns

### Phase 3: Subagent Creation (Optional Enhancement)
Create specialized subagent for practice planning:
```
practice-planning-agent:
  description: "Orchestrates practice plan creation"
  tools: [notion, hockey-coaching, youtube, hockey-diagram]
  workflow: [team-context, research, generate, create, share]
```

## Key Advantages of This Approach

1. **No Custom Code Required** - Uses existing MCP tools
2. **Natural Conversation** - No slash commands needed
3. **Flexible and Adaptable** - Easy to modify workflow
4. **Leverages AI Strengths** - Natural language understanding
5. **Maintains Context** - Conversation flow allows refinement
6. **Scalable** - Can add more MCP tools as needed

## Practice Guidelines Structure

```markdown
# PRACTICE_GUIDELINES.md

## Practice Time Allocations
- Warm-up: 15% (movement, fun, engagement)
- Skill Development: 40% (focus area drills)
- Team Concepts: 25% (systems, positioning)
- Game Simulation: 15% (scrimmage, situations)
- Cool-down: 5% (fun, positive ending)

## Age-Specific Considerations
### U8-U10
- Maximum 10 minutes per activity
- 2-3 activities happening simultaneously
- High activity, minimal standing
- Fun and engagement priority

### U12-U14
- 15-20 minutes per activity
- Can handle more complex instructions
- Introduction of systems play
- Competition elements

## Ice Utilization
- Split ice for multiple stations
- Maximize touches and repetitions
- Consider space for each drill
- Safety zones between activities

## Coaching Best Practices
- Clear, simple instructions
- Demonstrate first, explain second
- Positive reinforcement
- Safety reminders throughout
```

## Practice Plan Template Structure

```markdown
# PRACTICE_PLAN_TEMPLATE.md

# Practice Plan: [Team Name] - [Date]

## Practice Overview
- **Duration:** [X] minutes
- **Focus Areas:** [Primary focus], [Secondary focus]
- **Age Group:** [UXX]
- **Equipment Needed:** [List]

## Warm-up (X minutes)
### [Drill Name]
- **Setup:** [Diagram/Image]
- **Description:** [Clear instructions]
- **Coaching Points:** [Key focuses]
- **Variations:** [Progressions]

## Skill Development (X minutes)
### Station 1: [Focus Area]
[Drill details with visuals]

### Station 2: [Focus Area]
[Drill details with visuals]

## Team Concepts (X minutes)
[System work with diagrams]

## Game Simulation (X minutes)
[Scrimmage format and rules]

## Cool-down (X minutes)
[Fun activity to end positively]

## Coaching Notes
- Safety reminders
- Key teaching points
- Home practice suggestions
```

## MCP Tool Orchestration Pattern

```python
# Conceptual workflow (not actual code - just documentation)

1. Parse request → Extract (duration, age, focus)
2. Search team → mcp__notion-remote__search("Team Information")
3. Research drills → mcp__hockey-coaching__search_hockey_drills(query)
4. Research skills → mcp__hockey-coaching__search_hockey_skills(query)
5. Search videos → mcp__hockey-coaching__search_hockey_videos(query)
6. Read guidelines → Read("PRACTICE_GUIDELINES.md")
7. Read template → Read("PRACTICE_PLAN_TEMPLATE.md")
8. Generate plan → Structure drills into template
9. Create diagrams → mcp__hockey-diagram__generate_hockey_diagram(drill)
10. Upload images → mcp__cloudinary__upload(diagram)
11. Create page → mcp__notion-remote__create-pages(plan)
12. Share link → Present to user
13. Update plan → mcp__notion-remote__update-page(feedback)
```

## Error Handling Patterns

### MCP Tool Failures
- If Notion search fails → Ask for team details
- If hockey MCP fails → Use YouTube and web search
- If diagram generation fails → Use text descriptions
- If video search fails → Focus on written content

### Content Validation
- Verify age-appropriate content
- Check drill complexity matches skill level
- Ensure safety considerations included
- Validate time allocations sum to total

## Success Metrics

1. **Efficiency**: < 5 minutes to generate initial plan
2. **Quality**: Comprehensive plan with visuals
3. **Usability**: Coach can use directly at rink
4. **Adaptability**: Easy to modify based on feedback
5. **Consistency**: Follows best practices every time

## Future Enhancements

1. **Practice Database**: Track all plans and feedback
2. **Season Arc**: Connect practices to season goals
3. **Skill Tracking**: Monitor player development
4. **Video Library**: Build team-specific video collection
5. **Parent Communication**: Share practice highlights

This architecture provides a robust, scalable solution using Claude Code's existing capabilities without requiring custom development.