# 🏒 Hockey Practice Planning Workflows & Automation Guide

## Overview
This document defines the two core practice planning workflows with interactive steps, tool usage, and MCP prompt templates for automation in Claude Desktop.

---

## 📋 Workflow 1: Plan Next Practice (Interactive)

### Purpose
Generate a comprehensive practice plan based on previous practice feedback, skill coverage, and coach input at each step.

### Process Flow
Each step requires coach review and input before proceeding to the next.

---

### Step 1: Review Previous Practice & Get Coach Input
**Tools**: Airtable (Practice Sessions Log)

**LLM Actions:**
1. Query Airtable Practice Sessions Log for most recent entry
2. Extract and present:
   - Date and practice name
   - What worked well
   - Areas for improvement  
   - Success rating
   - Next practice focus recommendations
3. Query Practice Plans table for previous practice structure/timing

**Coach Input Required:**
- Confirm next practice date and duration
- Any specific focus areas based on recent games or observations?
- Expected attendance (affects station planning)
- Available coaches and their assignments
- Any equipment constraints?

**Output**: Context summary with coach priorities

---

### Step 2: Analyze Skill Coverage
**Tools**: Airtable (Skills Coverage Tracking)

**LLM Actions:**
1. Query Skills Coverage Tracking table
2. Sort all skills by "Last Practiced" date (null first, then oldest to newest)
3. Present skills in three categories:
   - **Never Practiced**: Skills with no practice date
   - **Not Recently** (14+ days): Skills that need attention
   - **Recently Practiced** (last 7 days): For awareness only

**Display Format:**
```
NEVER PRACTICED:
- Stationary Passing (Passing Skills category)
- Hockey IQ - Reading the Play (Hockey IQ category)
- Board Play Fundamentals (Body Contact category)

NOT RECENTLY (14+ days ago):
- [None currently - example]

RECENTLY PRACTICED (reference only):
- Edge Control - Aug 6 (1 time)
- Forward Skating - Aug 6 (1 time)
```

**Coach Input Required:**
- Which unpracticed skills are priorities for this practice?
- Any skills you want to emphasize even if recently practiced?
- Skills to deliberately skip this time?

**Output**: Priority skills list (typically 3-5 skills to focus on)

---

### Step 3: Smart Drill Selection
**Tools**: Airtable (Drill Favorites) + Hockey MCP

**LLM Actions:**
1. Review Drill Favorites table for existing drills that cover priority skills
2. Identify skill combinations that can be practiced together
3. Present drill options grouped by efficiency:

**Example Grouping:**
```
EFFICIENT DRILL COMBINATIONS:
Option A: "Figure 8 Edge Work" 
- Covers: Edge Control + Turning/Crossovers + Backward Skating
- Time: 7 minutes
- Rating: 5/5

Option B: "3 Station Skills - Passing"
- Covers: Stationary Passing + Receiving Passes + Give-and-go
- Time: 15 minutes  
- Rating: Not yet rated (new)

SINGLE SKILL DRILLS:
- "1v1 Defense vs Forward" - Individual Defense only
- Time: 7 minutes
- Rating: 4/5
```

**Coach Input Required:**
- Which drill combinations look good?
- Any drills from favorites you specifically want to include?
- Want to search MCP for alternatives to any of these?
- Time allocation preferences for each station/drill?

**MCP Search (if requested):**
- Search based on skill combinations identified
- Present 2-3 alternatives per skill group
- Focus on drills that cover multiple priority skills

**Output**: Selected drills list with time allocations

---

### Step 4: Generate Practice Plan
**Tools**: Previous practice structure as template + Claude generation

**LLM Actions:**
1. Retrieve previous practice plan structure from Airtable Practice Plans
2. Use as template, maintaining:
   - Overall time segments structure
   - Successful elements from "what worked well"
   - Water break placements
3. Modify based on:
   - Today's skill priorities
   - Selected drills
   - Coach's noted improvements
4. Generate complete practice plan

**Format:**
- Maintain same segment structure as previous practice
- Clear timing for each element
- Setup requirements
- Coaching points
- Equipment list

**Coach Input Required:**
- Review generated plan
- Any adjustments to timing?
- Swap any drills?
- Add/remove elements?

**Output**: Final practice plan (artifact)

---

### Step 5: Update Records
**Tools**: Airtable (Practice Plans) + Notion

**LLM Actions:**
1. Create new entry in Airtable Practice Plans table:
   - Practice Name
   - Date
   - Duration (minutes) - if tracked
   - Focus Areas (multi-select)
   - Skills Focus (multi-select)
   - Status: "Planned"
   - Equipment Needed
   - Link to previous practice
2. Present Notion page creation instructions
3. Confirm all updates completed

**Coach Input Required:**
- Confirm Airtable entry created correctly
- Any additional notes to add?

**Output**: Practice documented in system, ready for execution

---

## 📝 Workflow 2: Post-Practice Review & Update

### Purpose
Capture practice outcomes and prepare for next practice. Most updates happen automatically through table relationships.

### Process Flow

---

### Step 1: Create Practice Session Log
**Tools**: Airtable (Practice Sessions Log)

**LLM Actions:**
1. Create new entry in Practice Sessions Log
2. Link to today's Practice Plan (from Practice Plans table)
3. Auto-populate skills from plan

**Coach Input Required:**
- Actual attendance number
- Overall energy level (High/Medium/Low)
- Success rating (1-5)
- What worked well (bullet points)
- Areas for improvement (bullet points)
- Individual player notes (optional)
- Next practice focus recommendations

**Output**: Session log entry created

---

### Step 2: Rate Drills Used
**Tools**: Airtable (Drill Favorites)

**LLM Actions:**
1. List all drills used in practice (from Practice Plan)
2. For each drill, prompt for:
   - Effectiveness rating update (1-5)
   - Keep/Modify/Drop decision
   - Any coaching notes

**Coach Input Required:**
- Rating for each drill used
- Specific feedback or modifications needed

**Output**: Drill ratings updated

---

### Step 3: Automatic Updates (Confirm)
**Tools**: Airtable (automatic through relationships)

**Automatic Updates via Table Relationships:**
- **Skills Coverage Tracking**: "Last Practiced" and "Times Practiced" update automatically when linked through Practice Sessions Log
- **Drill Favorites**: "Last Used" and "Times Used" update automatically when linked through Practice Sessions Log
- **Practice Plans**: Status can be updated to "Completed"

**LLM Actions:**
1. Verify automatic updates have occurred
2. Display summary of what was updated

**Output**: Confirmation of all automatic updates

---

### Step 4: Summary for Next Practice
**Tools**: Analysis of inputs

**LLM Actions:**
1. Synthesize feedback into clear next steps
2. Identify skills that still need work
3. Suggest drill modifications
4. Create "Next Practice Focus" summary

**Output**: Clear recommendations for next practice planning session

---

## 🤖 MCP Prompt Templates

### Workflow 1: Plan Next Practice (MCP Prompt)
```python
@mcp.prompt
def plan_next_practice():
    """
    Interactive practice planning workflow for U10 hockey.
    
    STEP 1: Review Previous Practice
    - Query Airtable Practice Sessions Log for most recent entry
    - Query Practice Plans table for previous practice structure
    - Present findings to coach
    - ASK COACH: Practice date, duration, specific focus, attendance, coaches, equipment?
    - Wait for coach input before proceeding
    
    STEP 2: Analyze Skill Coverage  
    - Query Skills Coverage Tracking, sort by Last Practiced (nulls first)
    - Group skills: Never Practiced / Not Recently (14+ days) / Recently
    - Present organized skill list
    - ASK COACH: Which skills to prioritize? Any to skip?
    - Wait for coach input before proceeding
    
    STEP 3: Smart Drill Selection
    - Query Drill Favorites for drills covering priority skills
    - Group drills by skill efficiency (multi-skill drills preferred)
    - Present drill combinations with ratings and time
    - ASK COACH: Which drills to use? Need MCP search for alternatives?
    - If MCP search requested, search and present options
    - Wait for coach input before proceeding
    
    STEP 4: Generate Practice Plan
    - Use previous practice structure as template
    - Incorporate selected drills and timing
    - Maintain successful elements, improve noted areas
    - Generate complete practice plan artifact
    - ASK COACH: Any adjustments needed?
    - Wait for coach approval
    
    STEP 5: Update Records
    - Create entry in Airtable Practice Plans table
    - Include all fields: Name, Date, Duration, Focus Areas, Status="Planned"
    - Confirm updates completed
    - ASK COACH: Any additional notes?
    
    Tools Required:
    - Airtable: list_records, create_record
    - Hockey MCP: search_hockey_drills (if requested)
    - Artifacts: Create practice plan document
    
    Output: Complete practice plan with all systems updated
    """
```

### Workflow 2: Post-Practice Review (MCP Prompt)
```python
@mcp.prompt
def post_practice_review():
    """
    Post-practice review and update workflow.
    
    STEP 1: Create Practice Session Log
    - Create new entry in Practice Sessions Log
    - Link to today's Practice Plan
    - ASK COACH for:
      * Attendance number
      * Energy level (High/Medium/Low)
      * Success rating (1-5)
      * What worked well (bullets)
      * Areas for improvement (bullets)
      * Individual notes (optional)
      * Next practice focus
    - Wait for coach input
    - Create log entry with all information
    
    STEP 2: Rate Drills
    - List all drills from today's practice
    - For each drill, ASK COACH:
      * Effectiveness rating (1-5)
      * Keep/Modify/Drop?
      * Coaching notes?
    - Update Drill Favorites with ratings
    
    STEP 3: Verify Automatic Updates
    - Confirm Skills Coverage Tracking updated (via relationships)
    - Confirm Drill Favorites usage stats updated
    - Update Practice Plans status to "Completed"
    - Display summary of updates
    
    STEP 4: Prepare Next Practice Summary
    - Synthesize feedback into recommendations
    - Identify skills still needing work
    - Suggest drill modifications
    - Create "Next Practice Focus" summary
    
    Tools Required:
    - Airtable: list_records, create_record, update_records
    - Analysis: Synthesize feedback
    
    Output: Session logged, all tracking updated, next practice recommendations ready
    """
```

---

## 📊 Data Model Notes

### Practice Plans Table Fields
Current fields tracked:
- Practice Name
- Date  
- Duration (min) ✅ **(Yes, time is tracked)**
- Focus Areas (multi-select)
- Skills Focus (multi-select)
- Status
- Equipment Needed
- Practice Plan Link (to Notion)
- Season Phase
- Success Rating

### Automatic Relationship Updates
When Practice Sessions Log is created and linked:
- **Drill Favorites** automatically updates:
  - Last Used date
  - Times Used counter
  - Links to Practice Sessions
- **Skills Coverage Tracking** automatically updates:
  - Last Practiced date
  - Times Practiced counter
  - Links to related drills

---

## 💡 Implementation Tips

### For Interactive Workflows
- Coach stays engaged throughout process
- Each step builds on previous decisions
- Can skip back if needed to revise
- Clear pause points for input

### For Drill Efficiency
- Prioritize drills covering multiple skills
- Consider setup time between drills
- Group similar equipment needs
- Balance high/low energy activities

### For Continuous Improvement
- Previous practice structure provides template
- Successful elements preserved
- Problem areas addressed
- Progressive skill development maintained

---

## 🔧 Technical Implementation

### MCP Server Setup
The `hockey-prompts` MCP server will provide these workflows as reusable prompts through the `@mcp.prompt` decorator. This enables:
- Consistent workflow execution
- Integration with Claude Desktop
- Access to Airtable and Hockey MCP tools
- Interactive coach engagement at defined checkpoints

### Required Integrations
- **Airtable MCP**: For practice data management
- **Hockey MCP**: For drill search capabilities
- **Hockey Diagram MCP**: For visual drill representations
- **Notion MCP**: For documentation export

### Configuration
Add to both Claude Code CLI and Claude Desktop:
```json
{
  "hockey-prompts": {
    "command": "python",
    "args": ["/path/to/servers/hockey_prompts_mcp.py"]
  }
}
```