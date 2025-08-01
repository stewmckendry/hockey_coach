# Issue #7: Create Practice Plan Slash Command

## Overview
Develop a `/create-practice-plan` slash command (or subagent) that helps coaches create and edit practice plans by researching drills, structuring practices, and incorporating feedback. This will be an MVP feature for quick practice planning.

## Objectives
- Create intelligent practice plan generator
- Research drills from multiple sources
- Structure age-appropriate practices
- Allow editing of existing plans
- Output formatted for Notion publishing

## Command Functionality

### Command Syntax
```bash
# Create new practice plan
/create-practice-plan U10 "skating and passing" 60

# Edit existing practice plan
/edit-practice-plan [plan-url] "add more shooting drills"
```

### Parameters
- **Age Group**: U8/U10/U12/U14+
- **Focus Areas**: Skills to emphasize
- **Duration**: Practice length in minutes
- **Optional**: Team skill level, specific drills to include

## Implementation Architecture

### 1. Research Module
Sources to search:
- **Hockey MCP Tools**: Primary drill database
- **Local Drill Files**: Repository drill collection
- **Exa MCP**: Web search for innovative drills
- **YouTube MCP**: Video demonstrations

Research process:
```python
async def research_drills(focus_areas, age_group):
    # 1. Search Hockey MCP for relevant drills
    mcp_drills = await search_hockey_knowledge(
        query=f"{focus_areas} drills",
        age_groups=[age_group],
        n_results=20
    )
    
    # 2. Search local drill files
    local_drills = await search_drill_files(focus_areas)
    
    # 3. Exa search for additional ideas
    web_drills = await exa_search(
        f"youth hockey {age_group} {focus_areas} practice drills"
    )
    
    return combine_and_rank_drills(mcp_drills, local_drills, web_drills)
```

### 2. Practice Structure Module
Standard practice template:
```python
PRACTICE_STRUCTURE = {
    "warmup": {
        "duration_percent": 15,
        "drill_types": ["skating", "dynamic", "fun"]
    },
    "skill_development": {
        "duration_percent": 40,
        "drill_types": ["technique", "repetition"]
    },
    "team_concepts": {
        "duration_percent": 25,
        "drill_types": ["small_games", "systems"]
    },
    "game_simulation": {
        "duration_percent": 15,
        "drill_types": ["scrimmage", "competition"]
    },
    "cooldown": {
        "duration_percent": 5,
        "drill_types": ["fun", "shooting"]
    }
}
```

### 3. Plan Generation Module
```python
async def generate_practice_plan(params):
    # Research drills
    drills = await research_drills(params.focus_areas, params.age_group)
    
    # Structure practice
    plan = structure_practice(drills, params.duration)
    
    # Format for Notion
    notion_content = format_for_notion(plan)
    
    # Add coaching notes
    enhanced_plan = add_coaching_tips(notion_content, params.age_group)
    
    return enhanced_plan
```

### 4. Edit Functionality
```python
async def edit_practice_plan(plan_url, feedback):
    # Fetch existing plan
    current_plan = await fetch_notion_page(plan_url)
    
    # Parse feedback intent
    intent = analyze_feedback(feedback)
    
    # Modify plan based on feedback
    if intent.add_drills:
        new_drills = await research_drills(intent.drill_focus)
        updated_plan = incorporate_drills(current_plan, new_drills)
    elif intent.adjust_timing:
        updated_plan = rebalance_timing(current_plan, intent.timing_changes)
    
    return updated_plan
```

## Output Format

### Notion Practice Plan Template
```markdown
# Practice Plan: [Focus Areas]
**Date**: [Date]  
**Duration**: [X] minutes  
**Age Group**: U10  
**Focus**: [Primary skills]

## Equipment Needed 📋
- Pucks (30+)
- Cones (20)
- [Additional items]

## Practice Flow

### 1. Warm-Up (10 minutes) 🏃‍♂️
**[Drill Name]**
- Setup: [Brief description]
- Execution: [Key points]
- Coaching: [What to watch for]

### 2. Skill Development (25 minutes) 🎯
**Station 1: [Skill Focus]**
[Drill details with diagram reference]

**Station 2: [Skill Focus]**
[Drill details with diagram reference]

### 3. Team Concepts (15 minutes) 🤝
**[System or concept drill]**
[Description and key teaching points]

### 4. Game Time (8 minutes) 🏒
**Modified Scrimmage**
- Rules: [Special rules to reinforce focus]
- Goals: [What we're working on]

### 5. Cool Down (2 minutes) 🎯
**Fun Shooting Game**
[Quick, enjoyable finish]

## Key Coaching Points 💡
1. [Main teaching point]
2. [Secondary focus]
3. [Encouragement reminder]

## Progressions 📈
- Easier: [Modification for struggling players]
- Harder: [Challenge for advanced players]

## Safety Reminders ⚠️
- [Specific safety considerations]
```

## Integration Requirements

### File Structure
```
notion_team_site/
├── commands/
│   ├── create_practice_plan.py
│   └── edit_practice_plan.py
├── modules/
│   ├── drill_researcher.py
│   ├── practice_structurer.py
│   └── notion_formatter.py
└── drill_library/
    └── local_drills.json
```

### MCP Tool Integration
- Hockey MCP for drill search
- Notion MCP for page creation/editing
- Exa MCP for web research
- YouTube MCP for video links

## Success Criteria
- [ ] Command creates complete practice plans
- [ ] Researches from multiple sources
- [ ] Age-appropriate structure
- [ ] Edit functionality works
- [ ] Output ready for Notion
- [ ] 5-minute generation time max
- [ ] Includes safety considerations

## Future Enhancements (Post-MVP)
- Seasonal practice progression
- Skill assessment integration
- Practice plan library
- Team-specific customization
- Video drill demonstrations
- Printable practice cards

## Notes
- Keep MVP focused on core functionality
- Ensure drills are age-appropriate
- Include variety to maintain engagement
- Balance skill work with fun
- Always include safety reminders