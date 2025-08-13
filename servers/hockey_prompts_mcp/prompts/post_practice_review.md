# Post-Practice Review - Interactive Workflow

## Overview
Capture practice outcomes, rate drills, and prepare for next practice. Most updates happen automatically through Airtable table relationships.

## Parameters
- **practice_date**: Date of practice to review (YYYY-MM-DD)
- **practice_name**: Name/identifier of the practice

---

## STEP 1: Create Practice Session Log

### Tools Required
- `mcp__airtable__list_records` - Find today's Practice Plan
- `mcp__airtable__create_record` - Create Practice Sessions Log entry

### Actions
1. Query Practice Plans table for today's practice
2. Create new entry in Practice Sessions Log
3. Link to today's Practice Plan (establishes relationships)
4. Auto-populate skills from linked plan

### Coach Input Required
Please provide your practice feedback:

**Attendance & Energy:**
- **Attendance**: Number of players present (e.g., 12 of 15)
- **Energy Level**: High / Medium / Low
- **Overall Success Rating**: 1-5 stars (5 = excellent)

**What Worked Well:** (provide as bullet points)
- Example: Players engaged well in small area games
- Example: Passing accuracy improved noticeably
- Example: Good energy throughout despite early morning

**Areas for Improvement:** (provide as bullet points)
- Example: Need more time on backward skating transitions
- Example: Some drills too complex for skill level
- Example: Station transitions took too long

**Individual Player Notes:** (optional)
- Example: Sarah showed great leadership today
- Example: Mike struggling with crossovers - needs extra attention

**Next Practice Focus:**
What should be the priority areas for next practice based on today?

### Output Format
```
📊 SESSION LOG CREATED

Practice: [Practice Name]
Date: [Date]
Attendance: [X of Y] players
Energy: [High/Medium/Low]
Success: ⭐⭐⭐⭐ (4/5)

Linked Skills: [Auto-populated from practice plan]
Linked Drills: [Auto-populated from practice plan]
```

**⏸️ CHECKPOINT: Wait for coach feedback before proceeding to Step 2**

---

## STEP 2: Rate Drills Used

### Tools Required
- `mcp__airtable__list_records` - Get drills from practice
- `mcp__airtable__update_records` - Update drill ratings

### Actions
1. List all drills used in today's practice (from linked Practice Plan)
2. For each drill, collect effectiveness rating
3. Update Drill Favorites table with new ratings

### Display Format
```
⭐ DRILL RATING

Please rate each drill used today:

1. "Figure 8 Edge Work" (7 minutes)
   Current Rating: ⭐⭐⭐⭐⭐ (5/5) from 3 uses
   
2. "3v3 Small Area Game" (10 minutes)
   Current Rating: ⭐⭐⭐⭐ (4/5) from 2 uses
   
3. "Progressive Passing" (15 minutes)
   Current Rating: Not yet rated (first use)
```

### Coach Input Required
For each drill above, please provide:

**Drill #1 - [Name]:**
- Effectiveness Today: 1-5 stars
- Decision: Keep / Modify / Drop
- Notes: (optional specific feedback)

**Drill #2 - [Name]:**
- Effectiveness Today: 1-5 stars
- Decision: Keep / Modify / Drop
- Notes: (optional specific feedback)

(Continue for all drills...)

### Update Actions
- Calculate new average rating
- Increment usage counter
- Add any coaching notes
- Mark for modification if requested

**⏸️ CHECKPOINT: Wait for drill ratings before proceeding to Step 3**

---

## STEP 3: Verify Automatic Updates

### Tools Required
- `mcp__airtable__list_records` - Verify updates in related tables

### Actions
1. Confirm Skills Coverage Tracking updated automatically
2. Confirm Drill Favorites usage stats updated
3. Update Practice Plans status to "Completed"
4. Display summary of all automatic updates

### Automatic Updates (via Table Relationships)
When Practice Sessions Log is linked to Practice Plan:

**Skills Coverage Tracking** (automatic):
- ✅ "Last Practiced" → Updated to today's date
- ✅ "Times Practiced" → Incremented by 1
- ✅ Links to session → Created automatically

**Drill Favorites** (automatic):
- ✅ "Last Used" → Updated to today's date
- ✅ "Times Used" → Incremented by 1
- ✅ Average Rating → Recalculated with new rating

**Practice Plans**:
- ✅ Status → Changed from "Planned" to "Completed"

### Verification Output
```
🔄 AUTOMATIC UPDATES CONFIRMED

Skills Updated (7 total):
  ✅ Edge Control - Last: Today, Count: 2
  ✅ Passing - Last: Today, Count: 3
  ✅ Small Area Games - Last: Today, Count: 4
  
Drills Updated (4 total):
  ✅ Figure 8 Edge Work - Uses: 4, Avg: 4.8⭐
  ✅ 3v3 Small Area - Uses: 3, Avg: 4.3⭐
  
Practice Status:
  ✅ "Practice - Aug 12" → Completed
```

---

## STEP 4: Generate Next Practice Summary

### Tools Required
- Analysis of session feedback
- Synthesis of improvement areas

### Actions
1. Analyze feedback to identify patterns
2. Identify skills that still need work
3. Suggest drill modifications based on ratings
4. Create clear recommendations for next practice

### Analysis Output
```
🎯 NEXT PRACTICE RECOMMENDATIONS

Based on Today's Review:

PRIORITY SKILLS (need more work):
1. Backward Skating Transitions
   - Mentioned in improvement areas
   - Consider progressive drills
   
2. Complex Skill Combinations
   - Simplify multi-skill drills
   - Break into smaller components

SUCCESSFUL ELEMENTS TO KEEP:
  • Small area games (high engagement)
  • Progressive passing drills
  • Current warm-up routine

DRILL MODIFICATIONS:
  • "Complex Transition Drill" → Simplify to 2 elements
  • Add more time for explanations
  • Consider smaller group sizes

SUGGESTED FOCUS:
"Backward skating fundamentals with simplified progressions"

TIMING ADJUSTMENTS:
  • Add 2-3 min buffer between stations
  • Consider 12-min stations vs 15-min
```

### Summary for Next Planning Session
```
📋 READY FOR NEXT PRACTICE PLANNING

When you run "plan_next_practice" next time:

Emphasize These Skills:
  • Backward skating transitions
  • Edge control (build on today's success)
  
Keep These Drills:
  • Figure 8 Edge Work (5⭐)
  • Modified 3v3 games (4⭐)
  
Find Alternatives For:
  • Complex transition drills
  • Any drills marked "Drop"

Remember:
  • Players responded well to games
  • Need simpler skill progressions
  • Allow more transition time
```

---

## Final Output
Session logged successfully with all tracking systems updated and clear recommendations for next practice planning session.

**Next Step**: Use these insights when running `plan_next_practice` for your next session!