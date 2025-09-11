# Post-Practice Review - Interactive Workflow v2.0
*Updated: August 12, 2025 - Enhanced with template tracking and systems progress*

## Overview
Capture practice outcomes, rate drills, track systems progress, and prepare for next practice. Leverages Airtable relationships for automatic updates.

## Parameters
- **practice_date**: Date of practice to review (YYYY-MM-DD)
- **practice_name**: Name/identifier of the practice (auto-populated if possible)

---

## STEP 1: Create Practice Session Log

### Tools Required
- `mcp__airtable__list_records` - Find today's Practice Plan
- `mcp__airtable__create_record` - Create Practice Sessions Log entry
- `mcp__airtable__get_record` - Get Practice Template details (if used)

### Actions
1. Query Practice Plans table for today's practice
2. Pull template information if one was used
3. Create new entry in Practice Sessions Log
4. Link to today's Practice Plan (establishes relationships)
5. Auto-populate skills and drills from linked plan

### Enhanced Coach Input Required

**Basic Metrics:**
- **Attendance**: [# present] of [# rostered] players, [#] goalies
- **Energy Level**: High / Medium / Low
- **Overall Success Rating**: 1-5 stars
- **Template Performance** (if used): Did the template structure work? Y/N

**Segment-by-Segment Review:**
Based on your practice structure ([show segments from plan]):

**Segment 1: [Name] ([X] min)**
- What Worked: [specific observations]
- Issues: [any problems]
- Player Response: High/Medium/Low engagement

**Segment 2: [Name] ([X] min)**
- What Worked: [specific observations]
- Issues: [any problems]
- Player Response: High/Medium/Low engagement

[Continue for all segments...]

**Systems Progress** (if any were practiced):
- **[System Name]**: 
  - Understanding Level: Got it / Needs work / Too complex
  - Execution: Clean / Improving / Struggled
  - Ready for game? Y/N

**Overall Observations:**
- **Biggest Success**: [What went really well?]
- **Biggest Challenge**: [What was the main struggle?]
- **Surprise Discovery**: [Any unexpected learnings?]

**Individual Player Notes:**
- **Stars**: [Players who excelled]
- **Concerns**: [Players needing extra help]
- **Goalies**: [Specific goalie feedback]

**Next Practice Priority:**
Based on today, what's the #1 thing to work on next?

### Output Format
```
📊 SESSION LOG CREATED

Practice: [Practice Name]
Template Used: [Template Name or "Custom"]
Date: [Date]
Attendance: [X]/[Y] players, [Z] goalies
Energy: [High/Medium/Low]
Success: ⭐⭐⭐⭐ (4/5)

Segment Performance:
  • Segment 1: ✅ High engagement
  • Segment 2: ⚠️ Some confusion
  • Segment 3: ✅ Strong finish

Systems Progress:
  • Thunder Strong Breakout: Improving (70% ready)

Skills Auto-Linked: [Count] skills tracked
Drills Auto-Linked: [Count] drills to rate
```

**⏸️ CHECKPOINT: Wait for complete feedback before Step 2**

---

## STEP 2: Rate Drills & Progressions

### Tools Required
- `mcp__airtable__list_records` - Get drills from practice
- `mcp__airtable__update_records` - Update drill ratings and notes

### Actions
1. List all drills from today's practice with their progressions
2. Collect effectiveness rating for base drill AND progressions
3. Update Drill Favorites with ratings and progression notes

### Enhanced Display Format
```
⭐ DRILL & PROGRESSION RATING

━━━ SEGMENT 1 DRILLS ━━━

1. "Diagonal Skating Progressions" (20 min total)
   Previous Rating: New drill (first use)
   
   Rate each progression:
   • Basic forward turns: [1-5 stars]
   • Stop/starts added: [1-5 stars]
   • Pivots added: [1-5 stars]
   • Mohawks added: [1-5 stars]
   • With puck: [1-5 stars]
   • With obstacles: [1-5 stars]
   
   Overall Drill Rating: [1-5 stars]
   Time Management: Too long / Just right / Too short

━━━ SEGMENT 2 DRILLS ━━━

2. "Continuous Pass & Shoot Flow" (15 min)
   Previous Rating: New drill (first use)
   
   Rate progressions:
   • Basic pass-shoot: [1-5 stars]
   • With obstacle/deke: [1-5 stars]
   • Swedish 1v1 variation: [1-5 stars]
   
[Continue for all segments...]
```

### Coach Input Required
For each drill:

**Overall Assessment:**
- Base Effectiveness: 1-5 stars
- Best Progression: [Which worked best?]
- Weakest Progression: [Which needs work?]
- Decision: Keep as-is / Modify / Simplify / Drop
- Time allocation: Too long / Just right / Too short

**Modification Notes:**
- What specific changes for next time?
- Which progressions to skip with this age group?
- Setup improvements?

**⏸️ CHECKPOINT: Complete all drill ratings before Step 3**

---

## STEP 3: Update Systems & Skills Tracking

### Tools Required
- `mcp__airtable__update_records` - Update Thunder Playbook
- `mcp__airtable__list_records` - Verify skill updates

### Enhanced Actions
1. Update any practiced systems in Thunder Playbook:
   - Mastery Level progression
   - Add practice notes
   - Mark if game-ready
2. Verify Skills Coverage auto-updated
3. Check for skill gaps revealed during practice
4. Update Practice Plan status to "Completed"

### Systems Progress Tracking
```
🎯 SYSTEMS UPDATE

Thunder Strong Breakout:
  • Previous: Not Introduced
  • Now: Introduced (Aug 13)
  • Mastery: 60% - positions understood, execution needs work
  • Game Ready: Not yet
  • Next Steps: Add pressure, increase speed
  
[Other systems if applicable...]
```

### Skills Gap Analysis
```
⚠️ SKILLS GAPS IDENTIFIED

From Today's Practice:
  • Backward crossovers - weaker than expected
  • Passing accuracy - needs dedicated work
  • Gap control - defenders struggling
  
Not in Original Plan but Needed:
  • Stick handling in traffic
  • Communication/calling for puck
```

---

## STEP 4: Generate Enhanced Next Practice Recommendations

### Tools Required
- Analysis of all feedback
- Template performance data
- Systems progression needs

### Actions
1. Analyze segment-by-segment feedback
2. Identify template adjustments needed
3. Plan systems progression
4. Create specific, actionable recommendations

### Enhanced Analysis Output
```
🎯 NEXT PRACTICE BLUEPRINT

━━━ TEMPLATE RECOMMENDATION ━━━
Based on Today: Consider "Skill Development" template
Reason: Need fundamental work before more systems
Modification: Extend skill segments, shorten scrimmage

━━━ PRIORITY FOCUS AREAS ━━━

1. BACKWARD SKATING (Critical)
   - Struggled in today's progressions
   - Dedicate full station next practice
   - Simplify: C-cuts → Backward glide → Add speed
   
2. PASSING FUNDAMENTALS
   - Accuracy issues in flow drill
   - Start stationary before moving
   - Partner passing before team drills

3. THUNDER STRONG BREAKOUT (Continue)
   - Positions OK, execution needs work
   - Add: Walk-through review (3 min)
   - Progress: 50% speed reps
   - Not ready for full pressure yet

━━━ DRILL ADJUSTMENTS ━━━

KEEP BUT MODIFY:
  • "Diagonal Skating" → Only use first 4 progressions
  • "Pass & Shoot Flow" → Remove Swedish 1v1 for now
  
REPLACE:
  • "Progressive 2v1" → Too complex
  • Try: "2v0 Rush" first
  
TIME REALLOCATION:
  • Reduce: Scrimmage from 15 to 10 min
  • Add: Extra 5 min for skill work

━━━ STRUCTURAL CHANGES ━━━

Suggested Segments for Next Practice:
  1. Skating Focus (20 min) - emphasis backward
  2. Passing Stations (15 min) - stationary first
  3. System Review (10 min) - Thunder Strong at 50%
  4. Light Scrimmage (10 min) - apply concepts
  5. Extra water/transition time built in

━━━ COACHING ASSIGNMENTS ━━━

Based on Today's Needs:
  • Stewart: Lead passing stations (quality control)
  • Miro: Backward skating specialist
  • Dan L: Goalie + help strugglers

━━━ SUCCESS METRICS FOR NEXT PRACTICE ━━━

We'll know we succeeded if:
  ✓ 80% of players can execute backward crossovers
  ✓ Passing accuracy improves to 70%+
  ✓ Thunder Strong executed cleanly at 50% speed
  ✓ Energy stays high throughout
```

### Quick Reference Card
```
📋 NEXT PRACTICE QUICK CARD

Date: [Next practice date]
Template: Skill Development (modified)
Duration: 60 min (add transition buffers)

Must Do:
  • Backward skating fundamentals
  • Stationary passing before moving
  • Review Thunder Strong positions

Avoid:
  • Complex progressions
  • Too many concepts at once
  • Rushed transitions

Key Phrase: "Master basics before adding complexity"
```

---

## STEP 5: Create Draft Practice Plan for Next Session

### Tools Required
- `mcp__airtable__create_record` - Create draft Practice Plan
- `mcp__airtable__update_records` - Add blueprint notes

### Actions
1. Create new Practice Plans entry with:
   - Status: "Draft"
   - Date: [Next practice date]
   - Team: [Same team]
   - Practice Name: "Practice #[X] - DRAFT"
   - Notes: Full blueprint recommendations
   - Focus Areas: Based on identified priorities
   - Suggested Template: Link if recommended
   - Previous Practice: Link to today's practice
   
2. Save all recommendations in structured format
3. This becomes the starting point for next planning session

### Draft Practice Plan Created
```
📝 DRAFT PRACTICE PLAN CREATED

Record ID: rec_xxxxx
Status: Draft
Date: [Next practice date]

Pre-Populated:
  • Focus Areas: Backward Skating, Passing, Systems
  • Energy Level: Medium (skill development focus)
  • Template: Skill Development (modified)
  • Blueprint Notes: [Full recommendations saved]
  
When you run "plan_next_practice":
  → This draft will be your starting point
  → All recommendations readily available
  → Can modify or confirm the plan
```

### Communication Summary
```
📧 PARENT COMMUNICATION POINTS
(If needed for team update)

Today's Focus: [Main skills/systems worked on]
Progress Highlight: [Positive development]
Home Practice: [1-2 things players can work on]
Next Practice: [Date/time and what to expect]
```

---

## Final Output
```
✅ POST-PRACTICE REVIEW COMPLETE

All Systems Updated:
  • Practice Session: Logged
  • Drills: Rated with progression notes  
  • Skills: Auto-tracked
  • Systems: Progress recorded
  • Draft Practice Plan: Created for next session

Draft Practice ID: rec_xxxxx
Status: Ready for refinement

Key Takeaway: [One sentence summary]

Next Step: Run "plan_next_practice" which will:
  1. Load your draft plan
  2. Show the blueprint recommendations
  3. Allow modifications before finalizing
```

---

## Workflow Improvements in v2.0

### What's New:
1. **Segment-by-segment review** - More granular feedback
2. **Progression rating** - Not just drills, but each progression
3. **Template performance tracking** - Learn what structures work
4. **Systems progress tracking** - Clear mastery progression
5. **Skills gap identification** - Catch what wasn't planned but needed
6. **Enhanced recommendations** - Specific, actionable next steps
7. **Quick reference card** - Easy-to-scan next practice priorities
8. **Parent communication points** - Ready-to-share updates

### Benefits:
- Better continuity between practices
- More precise adjustments
- Template optimization over time
- Clear systems progression path
- Catches missed skills/development needs

---

*Post-Practice Review v2.0 - Enhanced based on Practice #2 experience*