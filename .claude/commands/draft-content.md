---
description: "Create draft coaching content pages from research findings, applying team context and UX Guidelines"
argument-hint: "<research-page-url-or-topic> [team-name] [custom-title]"
allowed-tools: ["mcp__notion-remote__search", "mcp__notion-remote__fetch", "mcp__notion-remote__create-pages", "mcp__notion-remote__update-page", "mcp__notion-remote__update-database", "Read", "TodoWrite"]
---

# Draft Content Command

Creates actionable hockey coaching content pages from research findings, transforming research insights into practical, age-appropriate coaching materials with team-specific customization.

## Content Creation Workflow

### Step 1: Research Integration
- Parse arguments to identify research page URL or topic
- If URL provided, fetch the research page directly
- If topic provided, search Content Library for matching research pages
- Extract research findings, teaching points, and safety considerations
- Identify age group and team context from research or arguments

**Error Handling:**
```
If research page not found:
  "No research found for '[input]'.
   
   To create quality content, please first run:
   /research-hockey '[topic]' [age-group]
   
   This ensures content is based on validated research."

If multiple research pages found:
  "Found [count] research pages for '[topic]':
   
   1. [Title 1] - Created [date]
   2. [Title 2] - Created [date]
   [...]
   
   Please specify which research to use by:
   - Providing the page URL
   - Being more specific about the topic"

If research page fetch fails:
  "Unable to access research page.
   Error: [specific error]
   
   Please verify:
   - The URL is correct
   - You have access to the page
   - Notion integration is working"

If Content Library inaccessible:
  "Warning: Cannot access Content Library database.
   
   Proceeding with direct page access only.
   Draft will be created but not tracked in Content Library."
```

### Step 2: Team Context Application
**Team-Specific Customization:**
- If team name provided, fetch from Team Information database
- Apply coaching philosophy to content tone and approach
- Integrate available equipment into drill selections
- Adjust complexity based on skill level
- Accommodate practice duration and ice time constraints
- Consider player count for activity organization

**Team Context Error Handling:**
```
If team not found:
  "Team '[team-name]' not found in Team Information database.
   
   Creating general content for [age-group].
   To add team context, first run:
   /setup-team '[team-name]' [age-group]"

If team fetch fails:
  "Unable to retrieve team information.
   Error: [specific error]
   
   Proceeding with age-group defaults only."
```

**Version Management:**
```
Before fetching team data:
  1. Always use mcp__notion-remote__fetch for latest version
  2. Check team's last_edited timestamp
  3. Use most recent team information for content creation
```

### Step 3: Content Transformation Strategy
**Research to Practice Translation:**
```
Transform research findings into:
- Step-by-step drill instructions
- Clear coaching cues and teaching points
- Age-appropriate progressions
- Safety reminders and equipment lists
- Game application scenarios
- Parent communication points
```

**Content Depth by Topic Type:**
- **Skill Development**: Progressive drills, common mistakes, coaching cues
- **Tactical Systems**: Positioning, roles, practice progressions
- **Practice Planning**: Time blocks, transitions, objectives
- **Physical Training**: Exercises, safety, age modifications
- **Mental Skills**: Concepts, exercises, game application

### Step 4: UX Guidelines Application
**Age-Appropriate Content Structure:**
```
U8 (8-9 years):
- 80% visual content placeholders/descriptions
- Simple 3-5 step instructions
- Fun activity names and themes
- 5-10 minute activity blocks
- Basic safety reminders

U10 (9-10 years):
- 70% visual content emphasis
- Clear progression steps
- Success indicators included
- 10-15 minute activities
- Skill "why" explanations

U12 (11-12 years):
- 60% visual/40% text balance
- Technical terminology with definitions
- Cause-and-effect explanations
- 15-20 minute sections
- System introduction elements

U14+ (13+ years):
- 50/50 visual-text balance
- Advanced tactical concepts
- Performance analysis elements
- 20-30 minute activities
- Mental game integration
```

## Draft Page Structure

### Standard Content Template
```
# [Topic] for [Age Group] - Draft

## Quick Reference 📋
- **Age Group**: [From research/team]
- **Duration**: [Time based on age attention span]
- **Equipment**: [From research + team available equipment]
- **Skill Level**: [From team context or general]
- **Safety Priority**: [Key safety point from research]
- **Source**: [Link to research page]

## Overview
[Engaging introduction using research findings]
[Why this matters for this age group]
[Connection to game situations]

## [Main Content Sections - Topic Dependent]

### For Skill Development Topics:
#### Skill Breakdown
[Progressive teaching points from research]
[Common mistakes to avoid]
[Age-appropriate technique cues]

#### Practice Activities
[2-3 drills adapted from research]
[Each with setup, execution, key points]
[Modifications for different skill levels]

#### Game Application
[How to use in game situations]
[Recognition cues for players]

### For Tactical Topics:
#### System Overview
[Visual description placeholder]
[Key positions and movements]
[Simple rules for age group]

#### Teaching Progression
[Stage 1: Walk-through]
[Stage 2: Passive pressure]
[Stage 3: Game speed]

#### Player Roles
[Position-specific responsibilities]
[Communication requirements]

### For Practice Planning Topics:
#### Practice Structure
[Warm-up activities]
[Main skill sections]
[Game/competitive elements]
[Cool-down approach]

#### Time Management
[Age-appropriate time blocks]
[Transition strategies]
[Energy management]

## Coaching Points 🎯
[Key teaching cues from research]
[Age-appropriate language and concepts]
[Positive reinforcement strategies]

## Safety Considerations ⚠️
[All safety points from research]
[Equipment checks needed]
[Supervision requirements]

## Adaptations 🔄
### Make it Easier
[Modifications for beginners]
[Reduced complexity options]

### Make it Harder  
[Challenges for advanced players]
[Added complexity elements]

## Parent/Player Communication 💬
[Key points to share with parents]
[Take-home concepts for players]
[Connection to long-term development]

## Next Steps 📈
[Progression to next skill/concept]
[Related topics to explore]
[Link back to research for reference]

---
*Draft created from research: [Research page link]*
*Team context: [Team name if applicable]*
*Ready for editing with /edit-content*
```

## Implementation Process

### Phase 1: Research and Context Gathering
1. Locate and fetch research page from arguments
2. Extract all research findings and recommendations
3. Identify topic type and content requirements
4. Fetch team context if team name provided
5. Create TodoWrite plan for content creation

### Phase 2: Content Planning
6. Determine optimal content structure for topic type
7. Plan sections based on research findings
8. Map research insights to practical applications
9. Apply age-appropriate content ratios
10. Design progressive difficulty elements

### Phase 3: Content Generation
11. Create page with "Draft" suffix in title
12. Generate overview connecting research to practice
13. Transform research findings into actionable content
14. Write clear, step-by-step instructions
15. Apply team-specific adaptations throughout

### Phase 4: Quality Enhancement
16. Add coaching points using appropriate terminology
17. Ensure safety considerations are prominent
18. Include adaptation options for different levels
19. Add parent/player communication elements
20. Create clear progression and next steps

### Phase 5: Documentation and Tracking
21. Create Content Library entry with Page Type: "Draft"
22. Link to source research page
23. Include team association if applicable
24. Set metadata for version tracking
25. Provide clear indication this is a draft

**Draft Creation Error Handling:**
```
If draft page creation fails:
  "Error creating draft page.
   Error: [specific error]
   
   Draft content has been prepared. Options:
   1. Retry page creation
   2. Create page manually and paste content
   3. Save draft locally"

If Content Library update fails:
  "Draft page created successfully but not tracked in Content Library.
   
   Page URL: [draft-page-url]
   
   You can manually add to Content Library or proceed without tracking."

If duplicate draft exists:
  "A draft already exists for this topic:
   '[Existing draft title]' created on [date]
   
   Would you like to:
   1. Create new draft anyway
   2. Update existing draft
   3. View existing draft"
```

**Version Control:**
```
When creating draft:
  1. Check for existing drafts on same topic
  2. Generate unique title with timestamp if needed
  3. Always link to source research page
  4. Include creation timestamp in metadata
  5. Set clear "Draft" status in title and properties
```

## Content Transformation Examples

### From Research Finding to Practice Content
```
Research Finding:
"U10 players benefit from cross-ice passing drills that emphasize 
accuracy over power, with success rates improving when targets 
are stationary before progressing to moving targets."

Draft Content:
#### Passing Accuracy Drill
**Setup**: Place 4 cones in a square, 10 feet apart
**Execution**:
1. Player stands in center with 5 pucks
2. Pass to each cone, trying to hit it directly
3. Count successful hits out of 5 attempts
4. Rotate to next player

**Key Points**:
- "Push the puck, don't slap it"
- "Point your stick where you want the puck to go"
- "Success = hitting 3 out of 5 cones"

**Progression**: After 80% success rate, replace one cone with a slowly skating player
```

## Error Handling

### No Research Found
```
"No research found for topic '[topic]'.
 To create quality content, please:
 1. First run: /research-hockey '[topic]' [age-group]
 2. Then run: /draft-content [research-page-url]
 
 This ensures content is based on validated research."
```

### Multiple Research Pages
```
"Found multiple research pages for '[topic]':
 1. [Research page 1 - date]
 2. [Research page 2 - date]
 
 Please specify which research to use by providing the page URL."
```

### Team Not Found
```
"Team '[team-name]' not found in Team Information database.
 Creating general content for age group.
 To add team context, first run: /setup-team '[team-name]' [age-group]"
```

## Success Criteria

- ✅ Draft page created with comprehensive coaching content
- ✅ All research findings effectively translated to practice
- ✅ Age-appropriate structure and language throughout
- ✅ Team context integrated where applicable
- ✅ Clear coaching points and safety considerations
- ✅ Practical adaptations for different levels
- ✅ Content Library tracking with proper metadata
- ✅ Clear indication this is a draft for editing
- ✅ No duplication of research phase work

## Workflow Integration

**Research → Draft → Edit → Publish Flow:**
```
1. /research-hockey "defensive zone coverage" U12
   → Creates: "Research: Defensive Zone Coverage - U12"

2. /draft-content [research-url] "Thunder Wolves"
   → Creates: "Defensive Zone Coverage for U12 - Draft"
   → Links to research page
   → Applies Thunder Wolves context

3. /edit-content [draft-url]
   → Will create final version
   → Applies UX Guidelines improvements
   → Creates: "Defensive Zone Coverage for U12"

4. /publish-page [final-url]
   → Makes content publicly available
```

## Example Usage

```bash
# Draft from research URL with team context
/draft-content https://notion.so/research-page-url "Thunder Wolves"

# Draft from topic search
/draft-content "power play breakout" "Storm Eagles"

# Draft without team context
/draft-content "skating fundamentals"

# Draft with custom title
/draft-content [research-url] "Thunder Wolves" "Our Special Teams Playbook"
```

The draft-content command transforms validated research into practical, actionable coaching content while maintaining clear separation between research gathering and content creation phases.