# Plan Next Practice - Interactive Workflow

## Overview
Generate a comprehensive practice plan based on previous practice feedback, skill coverage analysis, and coach input at each step.

## Parameters
- **practice_date**: Target date for practice (YYYY-MM-DD format)
- **duration_minutes**: Practice duration in minutes (default: 60)
- **age_group**: Age group for practice (e.g., U8, U10, U12)

---

## STEP 1: Review Previous Practice & Get Coach Input

### Tools Required
- `mcp__airtable__list_records` - Query Practice Sessions Log
- `mcp__airtable__list_records` - Query Practice Plans table

### Actions
1. Query Airtable Practice Sessions Log for most recent entry
2. Extract and present:
   - Date and practice name
   - What worked well
   - Areas for improvement
   - Success rating
   - Next practice focus recommendations
3. Query Practice Plans table for previous practice structure/timing

### Coach Input Required
Please provide the following information:
- **Practice Date**: Confirm date for next practice
- **Duration**: Total available ice time (minutes)
- **Specific Focus**: Any areas based on recent games or observations?
- **Expected Attendance**: Number of players (affects station planning)
- **Available Coaches**: How many coaches and their assignments?
- **Equipment Constraints**: Any limitations to consider?

### Output Format
```
📋 PREVIOUS PRACTICE SUMMARY
Date: [date]
Success Rating: [1-5] ⭐
What Worked: 
  • [point 1]
  • [point 2]
Areas to Improve:
  • [improvement 1]
  • [improvement 2]
Recommended Focus: [focus areas]
```

**⏸️ CHECKPOINT: Wait for coach confirmation before proceeding to Step 2**

---

## STEP 2: Analyze Skill Coverage

### Tools Required
- `mcp__airtable__list_records` - Query Skills Coverage Tracking table

### Actions
1. Query Skills Coverage Tracking table
2. Sort all skills by "Last Practiced" date (null first, then oldest to newest)
3. Group skills into three categories:
   - **Never Practiced**: Skills with no practice date
   - **Not Recently** (14+ days): Skills needing attention
   - **Recently Practiced** (last 7 days): For awareness only

### Display Format
```
🎯 SKILL COVERAGE ANALYSIS

NEVER PRACTICED:
  • Stationary Passing (Passing Skills)
  • Hockey IQ - Reading the Play (Hockey IQ)
  • Board Play Fundamentals (Body Contact)

NOT RECENTLY (14+ days ago):
  • Backward Crossovers - 21 days ago (2 times)
  • Defensive Positioning - 18 days ago (1 time)

RECENTLY PRACTICED (reference only):
  • Edge Control - Aug 6 (1 time)
  • Forward Skating - Aug 6 (1 time)
```

### Coach Input Required
- Which unpracticed skills are priorities for this practice?
- Any skills you want to emphasize even if recently practiced?
- Skills to deliberately skip this time?

**⏸️ CHECKPOINT: Wait for skill selection before proceeding to Step 3**

---

## STEP 3: Smart Drill Selection

### Tools Required
- `mcp__airtable__list_records` - Query Drill Favorites table
- `search_hockey_drills` - Search for drills (if requested)

### Actions
1. Review Drill Favorites table for drills covering priority skills
2. Identify skill combinations that can be practiced together
3. Present drill options grouped by efficiency

### Display Format
```
🏒 DRILL OPTIONS

EFFICIENT COMBINATIONS (Multiple Skills):
Option A: "Figure 8 Edge Work"
  • Skills: Edge Control + Turning/Crossovers + Backward Skating
  • Duration: 7 minutes
  • Rating: ⭐⭐⭐⭐⭐ (5/5)
  • Setup: Simple - cones only

Option B: "3 Station Skills - Passing"
  • Skills: Stationary Passing + Receiving + Give-and-go
  • Duration: 15 minutes
  • Rating: Not yet rated (new)
  • Setup: Moderate - nets and pucks

SINGLE SKILL DRILLS:
"1v1 Defense vs Forward"
  • Skills: Individual Defense
  • Duration: 7 minutes
  • Rating: ⭐⭐⭐⭐ (4/5)
  • Setup: Simple - cones and pucks
```

### Coach Input Required
- Which drill combinations look good?
- Any drills from favorites you specifically want to include?
- Want to search for alternative drills? (specify what you're looking for)
- Time allocation preferences for each station/drill?

### Optional MCP Search
If coach requests alternatives, search based on:
- Skill combinations identified
- Age group appropriateness
- Available equipment
- Time constraints

**⏸️ CHECKPOINT: Wait for drill selection before proceeding to Step 4**

---

## STEP 4: Generate Practice Plan

### Tools Required
- Previous practice structure as template
- Claude generation capabilities

### Actions
1. Retrieve previous practice plan structure from Airtable
2. Use as template, maintaining successful elements
3. Incorporate today's skill priorities and selected drills
4. Generate complete practice plan with:
   - Clear timing for each segment
   - Setup requirements
   - Coaching points
   - Safety considerations
   - Water break placements

### Practice Plan Template
```
🏒 PRACTICE PLAN - [Date]
Age Group: [U10]
Duration: [60] minutes
Focus: [Selected skills]

WARM-UP (10 min)
0:00-0:05 | Dynamic Stretching
  • [Specific movements]
  • Coaching: [Key points]
  
0:05-0:10 | Edge Work
  • [Drill details]
  • Setup: [Requirements]

SKILL STATIONS (35 min)
0:10-0:25 | Station 1: [Drill Name]
  • Skills: [List]
  • Setup: [Details]
  • Coaching Points: [Key focus]
  
0:25-0:30 | WATER BREAK

0:30-0:45 | Station 2: [Drill Name]
  • Skills: [List]
  • Setup: [Details]
  • Coaching Points: [Key focus]

GAME/SCRIMMAGE (10 min)
0:45-0:55 | [Game type]
  • Rules: [Modifications]
  • Focus: [Apply skills from practice]

COOL DOWN (5 min)
0:55-0:60 | Fun Activity + Stretch
  • [Activity details]
  • Team talk points

EQUIPMENT NEEDED:
  • [Complete list]

COACHING NOTES:
  • [Important reminders]
  • [Safety considerations]
```

### Coach Input Required
- Review generated plan - any timing adjustments?
- Want to swap any drills?
- Add or remove any elements?
- Confirm plan meets your needs

**⏸️ CHECKPOINT: Wait for plan approval before proceeding to Step 5**

---

## STEP 5: Update Records

### Tools Required
- `mcp__airtable__create_record` - Create Practice Plans entry
- `mcp__notion-remote__notion-create-pages` - Export to Notion (optional)

### Actions
1. Create new entry in Airtable Practice Plans table with:
   - Practice Name
   - Date
   - Duration (minutes)
   - Focus Areas (multi-select)
   - Skills Focus (multi-select)
   - Status: "Planned"
   - Equipment Needed
   - Link to previous practice

2. If requested, create Notion page with full practice plan

3. Confirm all updates completed

### Update Confirmation
```
✅ PRACTICE PLAN SAVED

Airtable Record:
  • ID: [record_id]
  • Name: Practice - [date]
  • Status: Planned
  • Skills: [list of selected skills]
  • Drills: [list of selected drills]

Notion Page (if created):
  • URL: [page_url]
  • Title: [practice_name]
  
Ready for Practice! 🏒
```

### Coach Input Required
- Confirm records created correctly
- Any additional notes to add?
- Want to export to Notion now?

---

## Final Output
Complete practice plan ready for on-ice execution with all tracking systems updated.