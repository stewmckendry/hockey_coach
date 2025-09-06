# ⚡ THUNDER HOCKEY TEAM SITE - MASTER DOCUMENTATION
*Version 1.0 - January 5, 2025*

## 🎯 Overview
This document serves as the single source of truth for the Ted Reeve Thunder U10A team Notion site. All parallel development sessions should reference this document to maintain consistency.

---

## 🏗️ CURRENT SITE STRUCTURE

### Home Page (Root)
- **ID**: `2660cdbf-4977-8099-a6bb-ccfc949f854b`
- **Name**: "⚡ Ted Reeve Thunder U10A"
- **Contains**: All three core databases

### Core Databases

#### 1. ⚡ Thunder Hockey Systems
- **Database ID**: `2660cdbf-4977-81ec-8ef1-e798971e7ae9`
- **Purpose**: Hockey systems/plays teaching defensive and offensive formations
- **Current Entries**: 1 (Defensive Zone Coverage)
- **View**: Gallery view with card layout

#### 2. ⚡ Thunder Drills  
- **Database ID**: `2660cdbf-4977-81b5-bc45-ec0d2a06b3dc`
- **Purpose**: Individual practice drills and exercises
- **Current Entries**: 3 (Dynamic Warm-Up, D-Zone Assignments & Coverage, 3v3 Battle)
- **View**: Table/Gallery hybrid

#### 3. 📅 Thunder Practice Plans
- **Database ID**: `2660cdbf-4977-8180-8f6e-ccdfc379025c`
- **Purpose**: Complete practice session plans
- **Current Entries**: 1 (September 2, 2025 practice)
- **View**: Calendar/Table view

---

## 📊 DATABASE SCHEMAS

### Hockey Systems Database (14 Properties)
```
Core Properties:
- Card Title (Title) - Primary identifier
- Card Number (Number) - Sequential ordering
- Play Nickname (Rich Text) - Fun team name like "Thunder Box"
- One Big Idea (Rich Text) - Core concept in one sentence
- Hero Image (Files) - Main diagram
- Zone (Select) - Defensive/Neutral/Offensive
- Play Type (Multi-select) - Coverage/Breakout/Forecheck/etc
- Complexity (Select) - ⚡ Basic, ⚡⚡ Intermediate, ⚡⚡⚡ Advanced
- Tags (Multi-select) - Searchable tags
- Video Links (URL) - YouTube tutorials
- Files & Media (Files) - Additional resources
- Additional Images (Files) - Extra diagrams

Relations:
- Related to Thunder Drills (Relation)
- Related to Practice Plans (Relation)
```

### Drills Database (16 Properties)
```
Core Properties:
- Drill Name (Title)
- Duration - mins (Number)
- Drill Type (Multi-select) - Skating/Passing/Shooting/Systems/Battle/etc
- Difficulty (Select) - ⚡ Easy, ⚡⚡ Medium, ⚡⚡⚡ Hard
- Players Required (Select) - 1-3/4-6/7-10/Full Team
- Positions Required (Multi-select) - Forward/Defense/Goalie/All Skaters
- Equipment Needed (Multi-select) - Pucks/Cones/Tires/Nets/Pylons
- Coaches Required (Number)
- Fun Factor (Select) - 😐 Okay, 😊 Fun, 🤩 Super Fun!
- Station Based (Checkbox)
- Last Used (Date)
- Video URL (URL)
- Media Preview (Files)

Relations:
- Related Systems (Relation to Systems DB)
- Related to Practice Plans (Relation)
```

### Practice Plans Database (17 Properties)
```
Core Properties:
- Practice Name (Title)
- Practice Date (Date)
- Location (Rich Text) - Arena/facility name
- Start Time (Rich Text) - Practice start time
- Duration - mins (Number)
- Practice Type (Select) - Regular/Game Day -1/Skills Only
- Season Phase (Select) - Preseason/Regular Season/Playoffs
- Status (Select) - Planned/Completed/Cancelled
- Focus Areas (Select) - Systems/Skills/Conditioning/Fun/Mixed
- Ice Zones Used (Multi-select) - Full Ice/Half Ice/Cross Ice/Stations
- Theme (Rich Text) - Practice theme/focus
- Coach Lead (Select) - Coach Stewart/Miro/Daniel/Dan
- 3rd Party Instructor (Checkbox)
- Notes (Rich Text)
- Additional Practice Media (Files)

Relations:
- Systems Covered (Relation to Systems DB)
- Drills (Relation to Drills DB)
```

---

## 🎨 UX STYLE GUIDE

### Visual Identity
- **Primary Colors**: Red (#DC2626), Black (#000000), Gray/Silver (#6B7280)
- **Team Identity**: "We bring the storm every shift, every game!"
- **Logo**: Red "T" with Thunder text on black circle with silver accents

### Emojis & Icons
```
Standard Usage:
⚡ - Thunder/Lightning (team identity, appears in all DB titles)
🔴 - Red (team color highlights)
⚫ - Black (team color accents)
🏒 - Hockey/Skills content
🥅 - Goal/Net references
🛡️ - Defense positioning
📅 - Schedule/Practice plans
🎯 - Objectives/Targets
🏆 - Achievement/Success
⭐ - Ratings/Levels
😊🤩 - Fun factor ratings
```

### Language Guidelines
- **Reading Level**: Grade 3-4 vocabulary
- **Sentence Length**: 10 words or less for instructions
- **Instructions**: Maximum 3 numbered steps per section
- **Tone**: Encouraging, positive, action-oriented
- **Thunder Phrases**: "Bring the storm!", "Thunder strikes!", "Lightning fast!"

### Content Hierarchy
1. **Visual First**: Large diagrams/images at top
2. **One Big Idea**: Bold, simple concept statement
3. **Position-Specific**: Separated by role (Forwards/Defense/Goalie)
4. **Progressive Levels**: Game-like progression system
5. **Tips & Don'ts**: Clear do/don't format

---

## 📝 CONTENT CREATION INSTRUCTIONS

### Creating a New System (Play Card)
1. **Duplicate Existing Entry**: Use "Defensive Zone Coverage" as template
2. **Required Elements**:
   - Hero diagram (Cloudinary hosted)
   - "One Big Idea" in 1 sentence
   - Position-specific instructions (3 points max each)
   - Thunder Tips for each position
   - Practice progression levels
   - When to use scenarios (3-4 checkboxes)
   - Coach's key points (3 max)

3. **Page Structure**:
```markdown
[Hero Image]
# SYSTEM NAME
## "Fun Nickname"
🎯 ONE BIG IDEA: [Single sentence]

## 📺 WATCH FIRST
[Video embed if available]

## 🏒 YOUR JOB (Pick Your Position)
### ⚡ FORWARDS
### 🛡️ DEFENSE  
### 🥅 GOALIE

## 🎮 PRACTICE LEVELS
- Level 1-5 progression

## 🎯 WHEN TO USE
- Game situation checkboxes

## 🏆 COACH'S KEY POINTS
- 3 key reminders
```

### Creating a New Drill
1. **Required Properties**:
   - Duration (5-20 minutes typical)
   - Drill Type (multi-select)
   - Equipment needed
   - Fun Factor rating
   - Difficulty level

2. **Page Content Structure**:
```markdown
## Drill Overview/Setup
- Time and objective

## Drill Diagram
[Image required]

## Setup
- Bullet points for setup

## Execution/How It Works
- Step by step instructions

## Key Points/Coaching Points
- Important reminders

## Variations (optional)
- Ways to modify drill
```

### Creating a New Practice Plan
1. **Required Info**:
   - Date, Location, Start Time
   - Duration (typically 60 mins)
   - Link to drills (usually 3-4)
   - Link to systems covered
   - Theme/focus

2. **Content Structure**:
```markdown
## Date | Time | Location

## Practice Theme
[Brief description]

## Drill Sequence
### Drill 1: [Name] (X mins)
[Full drill content or link]

### Drill 2: [Name] (X mins)
[Full drill content or link]

### Drill 3: [Name] (X mins)
[Full drill content or link]

## Equipment Needed
## Notes
```

---

## 🚧 COMING SOON - PLANNED DATABASES & PAGES

### 1. 📅 Game Schedule
**Purpose**: Track all games, tournaments, exhibitions
**Key Properties**:
- Game Date/Time
- Home/Away
- Opponent
- Arena/Location
- Game Type (Regular/Playoff/Tournament)
- Result
- Game Notes
- Related Practice Plans

### 2. 📢 Team Announcements
**Purpose**: News, updates, important information
**Key Properties**:
- Announcement Title
- Date Posted
- Category (News/Event/Reminder/Alert)
- Priority Level
- Content
- Attachments
- Author

### 3. 🏒 Games Database
**Purpose**: Game summaries, stats, highlights
**Key Properties**:
- Game Date
- Opponent
- Score
- Game Summary
- Stars of the Game
- Systems Used
- What Worked Well
- Areas to Improve
- Photos/Videos
- Related Practice Plans

### 4. 🏠 Enhanced Home Page
**Layout Plans**:
- Welcome banner with team logo
- Quick links to all databases
- Upcoming games widget
- Recent announcements
- This week's practice
- Team calendar embed
- Quick stats/standings

---

## 📁 ARCHIVED DOCUMENTATION
The following planning documents have been archived and should NOT be used for new development:

### Archived Files (Reference Only)
```
/team_site/docs/archived/
├── hockey_systems_database_plan.md (ARCHIVED - Initial planning)
├── thunder_play_card_system.md (ARCHIVED - V1 design)
├── notion_page_template_implementation.md (ARCHIVED - Old template approach)
├── notion_hockey_systems_database_schema.md (ARCHIVED - 40+ property version)
└── notion_defensive_zone_coverage_validation.md (ARCHIVED - Test page)
```

**⚠️ IMPORTANT**: These files contain outdated approaches. Only reference them for historical context.

---

## 🔄 WORKFLOW BEST PRACTICES

### For Parallel Development Sessions

1. **Before Starting**:
   - Read this entire document
   - Check current entry counts in each database
   - Use existing entries as templates

2. **Naming Conventions**:
   - Systems: "Play Type + Formation" (e.g., "Defensive Zone Coverage")
   - Drills: "Action + Skill" (e.g., "Dynamic Warm-Up")
   - Practices: "Thunder Practice - [Date]"

3. **Image Hosting**:
   - Use Cloudinary for all diagrams
   - Path format: `/hockey_diagrams/` or `/hockey_drills/`
   - Include date in filename when relevant

4. **Relations**:
   - Always link drills to related systems
   - Always link practices to drills used
   - Always link practices to systems covered

5. **Quality Checks**:
   - Verify all position instructions are present
   - Check reading level (Grade 3-4)
   - Ensure Thunder branding throughout
   - Test mobile view compatibility

---

## 🎯 SUCCESS METRICS

### Content Goals
- **Systems**: 20-25 total play cards by season end
- **Drills**: 40-50 drill library
- **Practices**: Full season of plans (30-40)

### Engagement Tracking
- Page views per entry
- Most used drills
- System mastery progression
- Parent/player feedback

---

## 📞 KEY CONTACTS & RESOURCES

### Notion Integration
- **Integration Token**: Available in Notion settings
- **Workspace ID**: Check Notion URL structure

### Development Resources
- **MCP Tools**: Use for all Notion API operations
- **Cloudinary**: For image hosting
- **YouTube**: For video examples

---

## 🔐 MAINTENANCE NOTES

### Version Control
- This is Version 1.0 (January 5, 2025)
- Update version number with major changes
- Keep changelog at bottom of document

### Regular Updates Needed
- Entry counts in database inventory
- New properties added to schemas
- New pages/databases created
- Workflow improvements discovered

---

## 📋 CHANGELOG

### Version 1.0 - January 5, 2025
- Initial documentation created
- Captured current state of 3 databases
- Documented UX guidelines and creation instructions
- Added future database plans
- Archived old planning documents

---

*END OF DOCUMENTATION - Use this as your single source of truth for Thunder site development*