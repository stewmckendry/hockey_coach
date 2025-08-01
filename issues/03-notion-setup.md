# Issue 3: Notion Database Structure & Templates

## Overview
Set up comprehensive Notion workspace infrastructure for hockey team content management. This includes database schemas, page templates, and organizational structure that supports the content creation workflow while maintaining consistency and accessibility.

## Objectives
- Create structured databases for team context and content management
- Build reusable page templates for different content types and age groups
- Establish content organization hierarchy and navigation
- Set up publishing workflow and permission management
- Create progress tracking and analytics framework

## Database Schemas

### 1. Team Context Database
**Purpose**: Store team-specific information and preferences for personalized content generation

```json
{
  "database_name": "Team Information",
  "properties": {
    "Team Name": {
      "type": "title",
      "description": "Official team name and designation"
    },
    "Age Group": {
      "type": "select",
      "options": ["U8", "U10", "U12", "U14", "U16", "U18"],
      "description": "Primary age category for content customization"
    },
    "Skill Level": {
      "type": "select", 
      "options": ["Beginner", "Intermediate", "Advanced", "Elite"],
      "description": "Overall team skill assessment"
    },
    "Season Goals": {
      "type": "multi_select",
      "options": [
        "Skill Development", "Team Chemistry", "Competition Success",
        "Fun & Engagement", "Individual Growth", "System Understanding",
        "Physical Conditioning", "Mental Toughness"
      ],
      "description": "Primary objectives for the season"
    },
    "Coaching Philosophy": {
      "type": "rich_text",
      "description": "Approach to coaching and player development"
    },
    "Practice Schedule": {
      "type": "rich_text",
      "description": "Regular practice times and frequency"
    },
    "Equipment Available": {
      "type": "rich_text",
      "description": "Training equipment and resources accessible"
    },
    "Ice Time Allocation": {
      "type": "rich_text",
      "description": "Available ice time and scheduling constraints"
    },
    "Communication Preferences": {
      "type": "select",
      "options": ["Email", "Team App", "Parent Portal", "Text Messages", "Notion Updates"],
      "description": "Preferred method for team communications"
    },
    "Parent Involvement Level": {
      "type": "select",
      "options": ["High", "Medium", "Low", "Varies"],
      "description": "Expected parent engagement and support"
    },
    "League/Organization": {
      "type": "rich_text",
      "description": "Hockey organization or league affiliation"
    },
    "Created Date": {
      "type": "created_time"
    },
    "Last Updated": {
      "type": "last_edited_time"
    }
  }
}
```

### 2. Content Management Database
**Purpose**: Track all content creation, status, and performance metrics

```json
{
  "database_name": "Content Library",
  "properties": {
    "Title": {
      "type": "title",
      "description": "Content title and identifier"
    },
    "Content Type": {
      "type": "select",
      "options": [
        "Drill", "Concept", "Practice Plan", "Team Guide", 
        "Rules", "Strategy", "Mental Game", "Conditioning"
      ],
      "description": "Category of content for organization"
    },
    "Section": {
      "type": "select",
      "options": [
        "Fundamentals", "Systems", "Conditioning", "Mental Game",
        "Rules & Conduct", "Equipment", "Safety", "Parent Resources"
      ],
      "description": "Main organizational section"
    },
    "Age Group": {
      "type": "multi_select",
      "options": ["U8", "U10", "U12", "U14", "U16", "U18", "All Ages"],
      "description": "Target age groups for content"
    },
    "Skill Focus": {
      "type": "multi_select",
      "options": [
        "Skating", "Shooting", "Passing", "Stickhandling", "Checking",
        "Positioning", "Tactics", "Goaltending", "Fitness", "Mental Skills"
      ],
      "description": "Primary skills developed by content"
    },
    "Difficulty Level": {
      "type": "select",
      "options": ["Beginner", "Intermediate", "Advanced", "Progressive"],
      "description": "Skill level requirement"
    },
    "Status": {
      "type": "select",
      "options": ["Draft", "Review", "Approved", "Published", "Archived", "Needs Update"],
      "description": "Current content state in workflow"
    },
    "Priority": {
      "type": "select",
      "options": ["High", "Medium", "Low"],
      "description": "Content importance and urgency"
    },
    "Public URL": {
      "type": "url",
      "description": "Published Notion page public link"
    },
    "Source Materials": {
      "type": "relation",
      "related_database": "Source References",
      "description": "Link to research and reference materials"
    },
    "Equipment Required": {
      "type": "multi_select",
      "options": [
        "Pucks", "Cones", "Sticks", "Goals", "Nets", "Boards",
        "Whistles", "Timers", "Pinnies", "Special Equipment"
      ],
      "description": "Equipment needed for drills/activities"
    },
    "Duration": {
      "type": "number",
      "description": "Time required in minutes"
    },
    "Player Count": {
      "type": "rich_text",
      "description": "Optimal and minimum player numbers"
    },
    "Created By": {
      "type": "created_by"
    },
    "Created Date": {
      "type": "created_time"
    },
    "Last Updated": {
      "type": "last_edited_time"
    },
    "View Count": {
      "type": "number",
      "description": "Page view analytics (manual tracking)"
    },
    "Team Feedback": {
      "type": "rich_text",
      "description": "Comments and suggestions from team"
    },
    "UX Guidelines Check": {
      "type": "checkbox",
      "description": "Confirms content meets UX guidelines"
    }
  }
}
```

### 3. Source References Database
**Purpose**: Track research sources and maintain content attribution

```json
{
  "database_name": "Source References",
  "properties": {
    "Source Title": {
      "type": "title",
      "description": "Name or title of the source material"
    },
    "Source Type": {
      "type": "select",
      "options": [
        "Thunder Playbook Data", "Web Article", "YouTube Video", 
        "Research Paper", "Hockey Manual", "Expert Interview",
        "USA Hockey Guidelines", "Coaching Course"
      ],
      "description": "Category of source material"
    },
    "URL": {
      "type": "url",
      "description": "Link to original source"
    },
    "Author/Organization": {
      "type": "rich_text",
      "description": "Creator or publishing organization"
    },
    "Date Published": {
      "type": "date",
      "description": "Original publication date"
    },
    "Credibility Rating": {
      "type": "select",
      "options": ["High", "Medium", "Low", "Unverified"],
      "description": "Assessment of source reliability"
    },
    "Key Insights": {
      "type": "rich_text",
      "description": "Main takeaways and relevant information"
    },
    "Related Content": {
      "type": "relation",
      "related_database": "Content Library",
      "description": "Content pieces that reference this source"
    },
    "Tags": {
      "type": "multi_select",
      "options": [
        "Research-Backed", "Practical", "Innovative", "Traditional",
        "Youth-Specific", "Professional-Level", "Safety-Critical"
      ],
      "description": "Categorization tags for easy filtering"
    },
    "Added Date": {
      "type": "created_time"
    }
  }
}
```

### 4. Publishing Analytics Database
**Purpose**: Track content performance and team engagement

```json
{
  "database_name": "Content Analytics",
  "properties": {
    "Content": {
      "type": "relation",
      "related_database": "Content Library",
      "description": "Link to tracked content"
    },
    "Publish Date": {
      "type": "date",
      "description": "When content was made public"
    },
    "Views": {
      "type": "number",
      "description": "Total page views (manual tracking)"
    },
    "Engagement Score": {
      "type": "select",
      "options": ["High", "Medium", "Low", "New"],
      "description": "Relative engagement assessment"
    },
    "Feedback Count": {
      "type": "number",
      "description": "Number of comments/feedback received"
    },
    "Share Count": {
      "type": "number",
      "description": "Times content was shared"
    },
    "Last Viewed": {
      "type": "date",
      "description": "Most recent known view date"
    },
    "Performance Notes": {
      "type": "rich_text",
      "description": "Observations about content performance"
    }
  }
}
```

## Page Templates

### 1. Team Context Page Template
```markdown
# [Team Name] - Season [Year]

## Team Overview 🏒
**Age Group**: [U8/U10/U12/etc.]
**Skill Level**: [Beginner/Intermediate/Advanced]
**League**: [Organization name]

## Our Goals This Season 🎯
1. [Primary goal]
2. [Secondary goal]  
3. [Additional goal]

## Coaching Philosophy 💭
[Description of coaching approach and values]

## Practice Information 📅
**Schedule**: [Regular practice times]
**Location**: [Rink/facility information]
**Duration**: [Typical practice length]

## Equipment & Resources 🥅
**Available Equipment**: 
- [List of training equipment]

**Required Player Equipment**:
- [Safety and basic equipment requirements]

## Communication 📢
**Primary Method**: [Preferred communication channel]
**Updates**: [How/when updates are shared]
**Questions**: [How parents/players can ask questions]

## Season Schedule 📆
[Link to detailed schedule or embedded calendar]

## Quick Links 🔗
- [Practice Plans Database]
- [Skills Development Resources]
- [Team Guidelines]
- [Parent Information]

---
*Last Updated*: [Date]
*Contact*: [Coach contact information]
```

### 2. Practice Plan Template (Age-Specific Variations)

#### U8-U10 Practice Plan Template
```markdown
# Practice Plan - [Date]
**Focus**: [Primary skill/concept] | **Duration**: [X] minutes | **Age**: U8-U10

## Today's Goals 🎯
1. [Simple, achievable goal]
2. [Fun-focused goal]
3. [Skill development goal]

## Equipment Check ✅
- [ ] Pucks
- [ ] Cones  
- [ ] [Other equipment]

## Warm-Up ([X] min) 🏃‍♀️
### [Activity Name]
[Simple description with large diagram]

**What Players Learn**: [Basic skill focus]
**Coach Focus**: [What to watch/encourage]

## Skill Station 1 ([X] min) 🏒
### [Drill Name]
[Step-by-step instructions with visuals]

**Key Points**:
- [Simple coaching point]
- [Encouragement focus]

## Fun Game ([X] min) 🎮
### [Game Name]
[Rules and setup - keep simple]

**Learning**: [What skill this reinforces]

## Skill Station 2 ([X] min) ⚡
### [Second Drill Name]
[Instructions with progression options]

## Scrimmage/Free Play ([X] min) 🥅
[Guidelines for unstructured play]

## Cool Down ([X] min) 🧘‍♀️
[Gathering and positive reinforcement]

## Coach Notes 📝
- **Safety Reminders**: [Key safety points]
- **Positive Focus**: [Encouragement themes]
- **Next Practice**: [Preview of next session]

---
**Equipment Used**: [List for setup/cleanup]
**Success Indicators**: [How to know practice went well]
```

#### U12+ Practice Plan Template
```markdown
# Practice Plan - [Date]
**Focus**: [Primary skill/system] | **Duration**: [X] minutes | **Age**: U12

## Practice Objectives 🎯
**Primary**: [Main learning objective]
**Secondary**: [Supporting skills/concepts]
**Application**: [Game situation focus]

## Equipment Setup 🛠️
- [ ] [Detailed equipment list]
- [ ] [Special setup requirements]

## Warm-Up ([X] min) 🔥
### [Dynamic warm-up name]
[Detailed instructions with progression]

**Technical Focus**: [Skill elements in warm-up]
**Intensity**: [Low/Medium/High]

## Skill Development Block 1 ([X] min) 🏒
### [Primary drill name]
**Objective**: [What this develops]
**Setup**: [Detailed diagram and positioning]
**Execution**: 
1. [Step 1 with technical details]
2. [Step 2 with coaching points]
3. [Step 3 with progression options]

**Coaching Points**:
- [Technical element 1]
- [Technical element 2]
- [Common mistake to correct]

**Progressions**:
- **Easier**: [Modification for struggling players]
- **Harder**: [Challenge for advanced players]

## Tactical Application ([X] min) 🧠
### [System/concept name]
**Game Context**: [When this applies in games]
**Key Concepts**: [Strategic understanding goals]

[Detailed breakdown with player movement diagrams]

## Competitive Drill ([X] min) ⚡
### [Competition name]
**Rules**: [Clear competition structure]
**Learning**: [Skills reinforced through competition]

## Scrimmage ([X] min) 🥅
**Focus**: [Specific application of practice themes]
**Coaching During Play**: [What to emphasize/correct]

## Debrief ([X] min) 💭
**Questions for Players**:
- [Question about main concept]
- [Question about application]

**Key Takeaways**: [Main points to remember]

## Post-Practice Notes 📋
- **Individual Notes**: [Space for player-specific observations]
- **Next Practice Preparation**: [Setup for following session]
- **Equipment Notes**: [What worked well/needs adjustment]

---
**Intensity Level**: [Overall practice intensity]
**Success Metrics**: [How to evaluate practice effectiveness]
```

### 3. Drill Instruction Template
```markdown
# [Drill Name]

## Overview 📋
**Purpose**: [What this drill teaches/develops]
**Age Group**: [Recommended ages]
**Duration**: [Typical time needed]
**Players**: [Optimal number and minimum required]
**Skill Level**: [Beginner/Intermediate/Advanced]

## Skills Developed 🎯
**Primary**: [Main skill focus]
**Secondary**: [Supporting skills]
**Game Application**: [How this applies in games]

## Equipment Needed 🛠️
- [Item 1 with quantity]
- [Item 2 with quantity]
- [Optional equipment for variations]

## Setup 🏗️
[Detailed diagram showing initial positioning]

**Ice Space**: [Area of rink used]
**Key Positions**: [Important markers/boundaries]
**Safety Considerations**: [Any safety setup requirements]

## Execution ▶️
### Step 1: [Action name]
[Detailed description with movement diagram]
**Player Focus**: [What players should concentrate on]
**Coach Focus**: [What coaches should watch/correct]

### Step 2: [Action name]  
[Detailed description with movement diagram]
**Timing**: [When this step occurs]
**Key Points**: [Critical technical elements]

### Step 3: [Action name]
[Detailed description with movement diagram]
**Success Indicator**: [How to know it's done correctly]

## Coaching Points 📝
**Technical Elements**:
- [Specific technique point 1]
- [Specific technique point 2]
- [Body position/stance focus]

**Common Mistakes**:
- [Mistake 1 and how to correct]
- [Mistake 2 and how to correct]

**Encouragement Focus**:
- [What to praise/reinforce]
- [How to maintain positive energy]

## Progressions & Variations 📈
### Beginner Modification
[Simpler version for developing players]
**Key Changes**: [What's modified and why]

### Standard Version
[Base drill as described above]

### Advanced Progression
[More challenging version]
**Added Elements**: [What makes it harder]

### Competition Version
[How to add competitive element]
**Scoring/Rules**: [Competition structure]

## Video Example 📹
[Embedded demonstration video]
**What to Watch For**: [Key elements highlighted in video]

## Troubleshooting 🔧
**If players struggle with [specific element]**:
- [Solution/modification]

**If drill breaks down**:
- [Reset strategy]

**If players lose interest**:
- [Engagement techniques]

## Related Drills 🔗
- [Link to similar/progressive drill]
- [Link to drill that builds on this one]
- [Link to game application drill]

---
**Source**: [Attribution if applicable]
**Last Updated**: [Date]
**Tested With**: [Age groups/teams where this has been used]
```

### 4. Concept Explanation Template
```markdown
# [Hockey Concept Name]

## What Is It? 🤔
[Clear, age-appropriate definition]

**Simple Explanation**: [One sentence summary]
**Why It Matters**: [Importance in hockey]

## Visual Example 📹
[Embedded video showing concept in action]
**Watch For**: [Key elements to observe in video]

## Breaking It Down 🔍
### Component 1: [Element name]
[Detailed explanation with diagram]
**Player Role**: [What individual players do]

### Component 2: [Element name]
[Detailed explanation with diagram]  
**Team Role**: [How team works together]

### Component 3: [Element name]
[Detailed explanation with diagram]
**Timing**: [When this happens]

## Game Situations 🏒
### When Do We Use This?
- [Situation 1 with context]
- [Situation 2 with context]
- [Situation 3 with context]

### Real Game Examples
[Description of how this looks in actual games]

## Practice Drills 🏃‍♀️
### Beginner Level
[Link to simple drill that teaches concept]

### Intermediate Level
[Link to more complex application drill]

### Game-Like Practice
[Link to drill that simulates real game usage]

## Key Points to Remember 💭
1. [Most important concept element]
2. [Second key point]
3. [Third key point]

## Common Mistakes ❌
### Mistake 1: [Common error]
**Why It Happens**: [Root cause]
**How to Fix**: [Correction strategy]

### Mistake 2: [Common error]
**Why It Happens**: [Root cause]
**How to Fix**: [Correction strategy]

## Questions to Ask Players 💬
- [Question that checks understanding]
- [Question that applies concept to game]
- [Question that encourages thinking]

## Parent Explanation 👨‍👩‍👧‍👦
[Simple explanation parents can understand and discuss with players]

## Next Steps 📈
**Once Players Understand This**:
- [Related concept to learn next]
- [Advanced application to work toward]

---
**Age Appropriateness**: [Which age groups this suits]
**Complexity Level**: [Beginner/Intermediate/Advanced]
**Related Concepts**: [Links to connected topics]
```

## Organizational Structure

### Workspace Hierarchy
```
[Team Name] Workspace
├── 🏒 Team Information (Database)
├── 📚 Content Library (Database) 
├── 🔗 Source References (Database)
├── 📊 Content Analytics (Database)
├── 📋 Practice Plans/
│   ├── Week 1-4: Foundation Skills
│   ├── Week 5-8: System Introduction  
│   ├── Week 9-12: Advanced Applications
│   └── Special Situations
├── 🎓 Skills Development/
│   ├── Skating Fundamentals
│   ├── Puck Skills
│   ├── Shooting & Scoring
│   ├── Defensive Play
│   └── Goaltending Basics
├── 🧠 Team Systems/
│   ├── Offensive Systems
│   ├── Defensive Systems
│   ├── Special Teams
│   └── Transitions
├── 📖 Team Guide/
│   ├── Team Rules & Expectations
│   ├── Equipment Guidelines
│   ├── Safety Protocols
│   └── Parent Information
└── 🎯 Resources/
    ├── Quick Reference Cards
    ├── Video Library
    ├── External Links
    └── Contact Information
```

### Navigation Setup
- **Main Dashboard**: Overview page with quick access to all sections
- **Age-Specific Views**: Filtered views showing only relevant content
- **Status Tracking**: Views showing content by status (draft, published, etc.)
- **Quick Actions**: Templates and shortcuts for common tasks

## Permission Management

### Access Levels
**Coach (Full Access)**:
- Create, edit, delete all content
- Manage team settings and databases
- Publish and unpublish content
- Access analytics and performance data

**Assistant Coach (Content Creator)**:
- Create and edit content
- Submit for review/approval
- Access team information
- View analytics (read-only)

**Team (View Only)**:
- Access published content only
- View practice plans and schedules
- Access team guide and resources
- No editing capabilities

**Parents (Limited View)**:
- Access parent-specific content
- View schedules and team information
- Access safety and equipment guidelines
- Team communication updates

## Implementation Workflow

### Initial Setup Steps
1. **Create Team Workspace**: Set up new Notion workspace
2. **Build Database Structure**: Create all four databases with properties
3. **Configure Templates**: Set up page templates for each content type
4. **Establish Navigation**: Create main dashboard and section organization
5. **Set Permissions**: Configure access levels for different user types
6. **Import Initial Content**: Populate with basic team information
7. **Test Publishing**: Verify public sharing works correctly

### Content Creation Workflow
1. **Planning**: Use team context to determine content needs
2. **Creation**: Use appropriate template for content type and age group
3. **Research Integration**: Link to source references database
4. **Quality Review**: Apply UX guidelines checklist
5. **Approval Process**: Move through status workflow
6. **Publishing**: Make public and update analytics tracking
7. **Performance Monitoring**: Track engagement and feedback

## Acceptance Criteria

### Database Functionality
- [ ] All four databases created with complete property schemas
- [ ] Database relationships function correctly (content ↔ sources)
- [ ] Filtering and sorting work for all key use cases
- [ ] Data validation prevents common input errors

### Template Usability
- [ ] Templates exist for all major content types
- [ ] Age-specific variations available for practice plans
- [ ] Templates include all required UX guideline elements
- [ ] Templates can be customized without breaking structure

### Organization & Navigation
- [ ] Clear hierarchy supports intuitive content discovery
- [ ] Search functionality works across all content
- [ ] Quick access to frequently used templates and tools
- [ ] Mobile navigation works smoothly

### Publishing & Permissions
- [ ] Public sharing creates clean, accessible URLs
- [ ] Permission levels function as specified
- [ ] Content approval workflow operates smoothly
- [ ] Analytics tracking captures key metrics

## Testing Requirements

### Functionality Testing
- Create sample content using each template
- Test database relationships and filtering
- Verify permission levels with different user accounts
- Validate public sharing and URL generation

### User Experience Testing
- Navigate workspace as different user types
- Test mobile accessibility and responsive design
- Verify search and filtering performance
- Confirm template customization doesn't break functionality

### Integration Testing
- Test compatibility with slash commands from Issue #1
- Verify UX guidelines from Issue #2 are properly integrated
- Confirm workflow supports content generation from Issue #5

## Timeline Estimate
**Total**: 1-2 hours
- Database creation and configuration: 45 minutes
- Template development: 30 minutes
- Testing and refinement: 15 minutes

## Dependencies
- UX guidelines from Issue #2 for template structure
- Integration requirements from Issue #1 (slash commands)
- Content workflow requirements from Issue #5

## Success Metrics
- Complete workspace setup in <2 hours
- All templates meet UX guideline requirements
- Content creation time reduced by 50% with templates
- 100% of content properly categorized and findable
- Publishing workflow achieves <5 minute draft-to-live time