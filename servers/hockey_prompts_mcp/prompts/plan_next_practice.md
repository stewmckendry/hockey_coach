# Plan Next Practice - Interactive Workflow v3.0
*Updated: August 12, 2025 - Includes Practice Templates and Hockey Systems integration*

## Overview
Generate a comprehensive practice plan using templates, systems focus, and skill coverage analysis. Streamlined workflow with integrated decision points.

## Parameters
- **practice_date**: Target date for practice (YYYY-MM-DD format)
- **duration_minutes**: Practice duration in minutes (default: pulled from Team table)
- **team**: Team name (auto-populated from active teams)

---

## STEP 1: Review Previous Practice & Template Selection

### Tools Required
- `mcp__airtable__list_records` - Check for Draft Practice Plans
- `mcp__airtable__list_records` - Query Practice Sessions Log
- `mcp__airtable__list_records` - Query Practice Templates table
- `mcp__airtable__list_records` - Query Thunder Playbook (Systems)
- `mcp__airtable__get_record` - Get Team information
- `mcp__notion__fetch` - Get Notion practice plan for structure reference

### Part A: Check for Draft Plan & Load Context
1. **CHECK FOR DRAFT PLAN FIRST**:
   - Query Practice Plans for Status="Draft" and upcoming date
   - If found, load blueprint recommendations from Notes field
   - Show as starting point for planning
2. **Auto-populate team context** from Teams table:
   - Team name, age group, level
   - Default practice duration
   - Coaching staff
3. Query Airtable Practice Sessions Log for most recent entry
4. Extract and present previous practice summary

### Part B: Template & Systems Selection

#### Display Format (with Draft Plan)
```
📢 DRAFT PLAN FOUND!

Draft for: [Date]
Created after: Practice #2 review
Recommended Focus: Backward Skating, Passing Fundamentals
Suggested Template: Skill Development (modified)

BLUEPRINT RECOMMENDATIONS:
━━━━━━━━━━━━━━━━━━━━━━━━
[Display saved blueprint notes]
━━━━━━━━━━━━━━━━━━━━━━━━

USE THIS DRAFT?
  1. Yes - Continue with draft recommendations
  2. Modify - Adjust the draft plan
  3. Start Fresh - Ignore draft, build new plan
```

#### Display Format (No Draft)
```
🏒 TEAM: Ted Reeves Thunder (U10 A)
Coaches: Stewart (Head), Miro, Dan L

📋 LAST PRACTICE: Aug 13 (Success: ⭐⭐⭐⭐)
What Worked: Progressive drills, high engagement
To Improve: Transition times, backward skating
Next Focus: [from session notes]

━━━━━━━━━━━━━━━━━━━━━━━━━

📘 PRACTICE TEMPLATES AVAILABLE:

1️⃣ SKILL DEVELOPMENT (50 min)
   Focus: Technical Skills, Position-Specific
   Structure: 18 min skills → 12 min battles → 15 min tactical
   Best For: Early season, after breaks, fundamental work
   
2️⃣ COMPETITIVE SYSTEMS (50 min)
   Focus: Tactical Systems, Battles/Compete
   Structure: 15 min positions → 15 min tactical → 15 min scrimmage
   Best For: Mid-season, game preparation
   
3️⃣ INTEGRATED GAME READY (50 min)
   Focus: Everything in one flow drill
   Structure: 20 min flow drill → 10 min special teams → 15 min scrimmage
   Best For: Day before games, limited ice time

4️⃣ CUSTOM (Build Your Own)
   Define your own segment structure

━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 HOCKEY SYSTEMS STATUS:

BREAKOUTS:
  ❌ Thunder Strong (Breakout 1) - Not Introduced
  ❌ Thunder Reverse - Not Introduced
  
ZONE ENTRIES:
  ❌ Thunder Speed (Entry 1) - Not Introduced
  ❌ Thunder Control - Not Introduced
  
DEFENSIVE ZONE:
  ❌ Thunder Box+1 - Not Introduced
  
SPECIAL TEAMS:
  ❌ Thunder PP Setup - Not Introduced
  ❌ Thunder PK Box - Not Introduced
```

### Coach Input Required
Please provide:
- **Practice Date**: [Date]
- **Duration**: [Default 60 min or custom?]
- **Template Choice**: (1, 2, 3, or 4-Custom)
  - If Custom: Provide segment breakdown (e.g., "20-15-15-10")
- **Systems Focus**: Which systems to introduce/practice? (can be none)
- **Expected Attendance**: [# players, # goalies]
- **Available Coaches**: [Who and assignments?]
- **Special Considerations**: [Equipment, specific player needs, etc.]

**⏸️ CHECKPOINT: Wait for template selection and basic inputs**

---

## STEP 2: Skill Analysis & Segment Mapping (Template-Aware)

### Tools Required
- `mcp__airtable__list_records` - Query Skills Coverage Tracking table (ALL 37 skills)
- `mcp__airtable__get_record` - Get selected Practice Template details

### Pre-Analysis: Load Complete Skill Inventory
**CRITICAL**: Query and load ALL 37 skills from Skills Coverage Tracking
- Store skill names, categories, and Skill Components in memory
- Note "Last Practiced" dates and "Times Practiced" counts
- This will be used for comprehensive mapping in Step 5

### Actions
1. If template selected (1-3), pull template structure and adapt
2. If custom or systems focus, build appropriate structure
3. Map skills to segments based on template + coach priorities
4. Integrate any selected systems into appropriate segments
5. **Flag overdue skills** (not practiced in 2+ weeks for Critical skills)

### Display Format (Example with Template #2 - Competitive Systems)
```
📊 PRACTICE PLAN STRUCTURE - COMPETITIVE SYSTEMS TEMPLATE

━━━ SEGMENT 1: Position Stations (15 min) ━━━

DEFENSE STATION (7.5 min):
Skills to Cover:
  • Gap Control ⚠️ (not recent)
  • Backward Skating ⚠️ (21 days ago)
  • Angling/Positioning
  
FORWARD STATION (7.5 min):
Skills to Cover:
  • Attack Moves
  • Shooting in Stride
  • 1v1 Dekes

━━━ SEGMENT 2: Tactical Battles (15 min) ━━━

SYSTEM INTEGRATION:
  ✅ Thunder Strong Breakout (introducing today)
  - Walk through first
  - Then apply in 2v2 battles
  
Skills Reinforced:
  • Passing under pressure
  • Quick decisions
  • Battle/compete

━━━ SEGMENT 3: Scrimmage (15 min) ━━━

Focus:
  • Apply Thunder Strong breakout
  • Stop for teaching moments
  • Reinforce positioning

━━━━━━━━━━━━━━━━━━━━━━━━━

SKILLS COVERAGE SUMMARY:
✅ Addressing overdue: Backward skating, gap control
✅ System introduction: Thunder Strong breakout
✅ Template maintains: Position development + compete
```

### Coach Input Required
- Approve this structure OR request modifications
- Confirm system integration points
- Any specific skill priorities within template?

**⏸️ CHECKPOINT: Get approval before drill selection**

---

## STEP 3: Smart Drill Selection (Always Research-Based)

### Tools Required
- `mcp__airtable__list_records` - Query Drill Favorites table (PRIMARY)
- `search_hockey_drills` - Search drill library (PRIMARY)
- `search_hockey_videos` - Find video demonstrations
- `search_hockey_tactics` - Get system-specific drills
- Template's Sample Drills - For reference only (not prescriptive)

### Actions
1. **ALWAYS research drills** for each segment's skills:
   - Query your Drill Favorites for matching skills
   - Search hockey MCP tools for best options
   - Use template drill names as search hints only
2. Present comprehensive options to coach
3. For systems work, find specific system drills
4. Let coach select from researched options

### IMPORTANT
**Template drills are EXAMPLES ONLY.** Always:
- Search your favorites first
- Use hockey MCP tools for comprehensive options  
- Present multiple choices to the coach
- Template suggestions are just starting points for research

### Display Format
```
🏒 DRILL RESEARCH FOR COMPETITIVE SYSTEMS TEMPLATE

━━━ SEGMENT 1: Position Stations (15 min) ━━━
Target Skills: Gap Control, Backward Skating, Angling

DEFENSE STATION OPTIONS:

YOUR FAVORITES (from Airtable):
✅ "1v1 Defense vs Forward" 
  • Rating: ⭐⭐⭐⭐ (4/5) | Used: 5 times
  • Covers: Gap control, angling
  • Duration: 7 minutes
  
✅ "Backward Power Skating"
  • Rating: ⭐⭐⭐⭐⭐ (5/5) | Used: 3 times
  • Covers: Backward skating, transitions
  • Duration: 8 minutes

LIBRARY RESEARCH (from hockey MCP):
📚 "Gap Control Progression" 
  • Source: Hockey Canada Drill Hub
  • Complexity: Progressive (3 levels)
  • Perfect for: U10 age group
  
📚 "Defensive Skating Circuit"
  • Source: USA Hockey ADM
  • Includes: Backward, pivots, gap
  • Equipment: 6 cones

📚 "Angling Drill - Board Play"
  • Source: CoachThem Library
  • Focus: Body position, stick on puck
  • Pairs well with gap control

(Template mentioned "Gap Control Progression" - found similar options above)

FORWARD STATION OPTIONS:
[Continue with actual research...]

━━━ SEGMENT 2: Tactical Battles (15 min) ━━━

SYSTEM DRILL RESEARCH:
📚 Searched for "breakout drills" and "D-to-D passing":
  • "Progressive Breakout Drill" - 5 phases
  • "Thunder Strong Specific" - walk through included
  • "2v2 Breakout Battles" - competitive element

[Continue with all segments...]
```

### Coach Input Required
- **Which drills from the research do you prefer?**
- Want details on any specific drill?
- Need video demonstrations?
- Any drills you want to modify or combine?

**⏸️ CHECKPOINT: Coach selects from researched options**

---

## STEP 4: Generate Practice Plan

### Tools Required
- Selected template structure
- Approved drills and systems
- Notion format template

### Actions
1. Generate plan following template structure
2. Include system teaching points prominently
3. Add progression notes for new systems
4. Format for both Airtable and Notion

### Practice Plan Output
```
🏒 TED REEVES THUNDER - PRACTICE #3
📅 August 14, 2025 | ⏱️ 50 minutes | 👥 U10 A
📘 Template: COMPETITIVE SYSTEMS

━━━━━━━━━━━━━━━━━━━━━━━━━
📋 PRACTICE OVERVIEW
Focus: Position skills + Thunder Strong Breakout
New System: Thunder Strong (Breakout 1)
Emphasis: Compete level with tactical execution
Expected: 12 players, 1 goalie
Coaches: Stewart (Forwards), Miro (Defense), Dan L (Goalie/Float)

Equipment Needed:
• Pucks (lots)
• 15-20 cones for positioning
• 2 nets
• Whiteboard for system diagram

━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 NEW SYSTEM: THUNDER STRONG BREAKOUT

[Diagram placeholder]

Key Points:
1. D retrieves, looks D-to-D first
2. Strong-side winger at hash marks on boards
3. Center swings low for support
4. Weak-side winger stays high
5. If covered, use center outlet

━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ PRACTICE TIMELINE

[Detailed timeline following template...]

━━━━━━━━━━━━━━━━━━━━━━━━━
"Systems create structure, compete creates champions!" ⚡
```

**⏸️ CHECKPOINT: Final approval before saving**

---

## STEP 5: Update Records with Comprehensive Skill Mapping

### Tools Required
- `mcp__airtable__create_record` - Create Practice Plans entry
- `mcp__airtable__update_records` - Batch update Skills Coverage Tracking
- `mcp__airtable__update_records` - Update system introduction dates
- `mcp__notion__create_page` - Create formatted practice plan

### Actions

#### 1. Create Practice Plans Entry
- Link to Practice Template used
- Link to Thunder Playbook systems introduced  
- All standard fields (Team, Drills, etc.)

#### 2. COMPREHENSIVE SKILL MAPPING (Critical Step)

**For EACH drill in the practice plan:**

a) **Deep Skill Analysis** - Examine the drill description and identify:
   - **Primary Skills**: Core focus of the drill (2-3 skills max)
   - **Secondary Skills**: Supporting skills practiced (3-5 skills)
   - **Incidental Skills**: Any other skills touched on (2-3 skills)

b) **Component-Level Matching** - For each skill in Skills Coverage Tracking:
   - Read the "Skill Components" field
   - Match drill activities to specific components
   - If 2+ components match, include that skill

c) **Batch Update Process** - Use update_records for efficiency:
   ```
   PASS 1: Analyze all drills, create master skill list
   PASS 2: Update skills 1-10 with batch update_records
   PASS 3: Update skills 11-20 with batch update_records  
   PASS 4: Update remaining skills if needed
   ```

d) **Update Fields for Each Matched Skill**:
   - Set "Last Practiced" to practice_date
   - Increment "Times Practiced" by 1
   - Add drill record ID to "Related Drills" array

**SKILL MAPPING RULES:**
- Skating drills → Check ALL skating skills + Balance/Agility
- Passing drills → Check passing skills + Hockey IQ skills + Receiving
- Shooting drills → Check shooting skills + Puck Control in Motion
- Battle/compete drills → Check Physical Play + all Defensive skills
- Systems drills → Check Hockey IQ + Positional Play + relevant technical skills
- Flow drills → Check 8-12 skills minimum (they touch everything)
- Small area games → Check 6-10 skills (multiple elements)

**Example Skill Mapping for "2v2 Breakout Battles":**
```
Primary Skills:
• Defensive Zone Play (breakout focus)
• Team Defense Systems (2v2 structure)
• Moving Passes (outlet passes)

Secondary Skills:  
• 1v1 Defense & Gap Control (defending in 2v2)
• Puck Control in Motion (carrying puck out)
• Hockey IQ - Reading the Play (decisions)
• Communication (calling for puck)

Incidental Skills:
• Forward Skating & Acceleration (racing for pucks)
• Backward Skating (defensive tracking)
• Physical Play Fundamentals (board battles)
```

#### 3. Update Thunder Playbook Table
- Mark system as "Introduced" with date
- Link to practice plan

#### 4. Create Notion Page
- System diagrams/teaching points
- Full formatted plan

### Update Confirmation with Full Skill Tracking
```
✅ PRACTICE PLAN SAVED WITH COMPREHENSIVE TRACKING

Airtable Updates:
• Practice Plan: rec_xxxxx
• Template Used: Competitive Systems
• System Introduced: Thunder Strong Breakout

SKILLS COVERAGE UPDATED (18 skills mapped):

Segment 1 - Position Stations:
  Defense Station (6 skills updated):
  ✓ 1v1 Defense & Gap Control
  ✓ Backward Skating  
  ✓ Angling & Body Positioning
  ✓ Stops, Pivots & Transitions
  ✓ Edge Control
  ✓ Hockey IQ - Reading the Play
  
  Forward Station (5 skills updated):
  ✓ Puck Control in Motion
  ✓ Deking and Fakes
  ✓ Fundamental Shots
  ✓ Forward Skating & Acceleration
  ✓ Balance and Agility

Segment 2 - Tactical Battles (7 skills updated):
  ✓ Defensive Zone Play
  ✓ Moving Passes
  ✓ Team Defense Systems
  ✓ Hockey IQ - Reading the Play
  ✓ Physical Play Fundamentals
  ✓ Communication
  ✓ Positional Play

Notion Page:
• URL: https://notion.so/[page_id]
• Includes: System diagram and skill heat map

🎯 Ready for Practice!
Next: Run post_practice_review after practice
```

---

## Workflow Benefits with Templates & Systems

### Templates Provide:
1. **Proven structures** that work for specific goals
2. **Time allocation** guidance
3. **Appropriate drill suggestions**
4. **Segment flow** that makes sense

### Systems Integration Adds:
1. **Progressive introduction** of team tactics
2. **Tracking** of what's been taught
3. **Consistency** in teaching approach
4. **Game-ready** preparation

### Time Savings:
- With templates: **Target <10 minutes** for planning
- Templates eliminate structure decisions
- Systems tracking prevents redundancy
- Drill suggestions reduce search time

### Flexibility Maintained:
- Can still go full custom (Option 4)
- Templates are starting points, not rigid rules
- Systems can be mixed into any template
- Coach maintains full control

---

*Workflow v3.0 - Enhanced with Practice Templates and Hockey Systems*