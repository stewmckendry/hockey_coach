# From the Rink to the Terminal: How AI Helped Me Coach Smarter, Not Harder

It's 9 PM on a Thursday. Tomorrow's practice is at 6 AM. I'm staring at a blank practice plan, knowing I need drills for 20 nine-year-olds at different skill levels, an email update for parents about the weekend tournament, and somehow need to make it all fun while teaching proper defensive zone coverage. 

Welcome to volunteer coaching in competitive youth hockey.

If you've been following Coaching the Machine, you know I took the summer off from writing. But I never stopped building. While my son Liam and his teammates were making memories at baseball provincials, I was quietly assembling a suite of AI tools for his upcoming hockey season—his first year playing 'A' level in the GTHL.

What started as a simple question—"Can AI help me be a better volunteer coach?"—turned into something much more interesting. And applicable far beyond the rink.

## The Game Changer: Claude Code

First, let me share the biggest unlock of the past few months: I switched my development environment to Claude Code. If you haven't tried it yet, let me show you what I mean:

```bash
> claude "Help me search for passing drills in my hockey knowledge base"

Claude: I'll help you search for passing drills. Let me use the hockey MCP server to find relevant drills.

> Searching for: "passing drills U10"...
> Found 47 results
> Filtering by complexity and age group...
```

*[VIDEO PLACEHOLDER: 2-minute demo showing Claude Code helping build a search function, with terminal commands and real-time file editing]*

In one evening, I went from idea ("I need searchable drills") to working implementation. No Stack Overflow. No debugging for hours. Just conversation and code.

*[SCREENSHOT PLACEHOLDER: Claude Code terminal showing the conversation flow and generated code side-by-side]*

## Problem #1: The Knowledge Maze

Let me show you exactly what I mean. Here's what Tuesday night looked like before:

**9:15 PM:** Open Hockey Canada PDF (247 pages)  
**9:18 PM:** Search for "passing" - 73 results  
**9:22 PM:** Find a drill that might work, but it's for U14  
**9:25 PM:** Open bookmark folder "Hockey Drills" - 47 saved links  
**9:28 PM:** Click through three broken links  
**9:31 PM:** Find a decent drill but no idea if we've run it recently  

Here's Tuesday night now:

```python
# Actual query to my Hockey Knowledge MCP
result = hockey_mcp.search_drills(
    query="passing drills for U10 that work on give-and-go in neutral zone",
    filters={
        "age_group": "U10",
        "skills": ["passing", "timing"],
        "complexity": "medium",
        "duration": "8-10 minutes"
    }
)

# Returns:
{
    "drill": "PASSING – PASS AND MOVE #3",
    "equipment": "Pucks, Nets, 6 cones",
    "setup": "Players in opposite corners, coach at center ice",
    "teaching_points": [
        "Tape-to-tape passes",
        "Present stick as target",
        "Quick feet after pass"
    ],
    "progression": "Start stationary, add movement, then add defender",
    "diagram_url": "generated_diagram_123.svg"
}
```

*[VIDEO PLACEHOLDER: Live search showing natural language query returning specific drills with teaching points]*

The knowledge base contains:
- **1,247 drills** from Hockey Canada, USA Hockey, and top coaches
- **89 complete practice plans** organized by theme
- **156 skill progressions** from learn-to-skate to elite
- **43 team systems** (breakouts, forechecks, power plays)

*For my business leader friends: Imagine your company's SOPs, best practices, and institutional knowledge available through conversation instead of search.*

## Problem #2: The Whiteboard Translation

Here's what happened when I first asked AI to create a hockey diagram:

```
Me: "Draw a 2-1-2 forecheck diagram"

ChatGPT: [Produces ASCII art that looks like a failed game of Tetris]

Me: "Generate an image of a 2-1-2 forecheck"

DALL-E: [Creates beautiful artwork of... stick figures on a blue blob?]
```

*[IMAGE PLACEHOLDER: Side-by-side comparison of AI-generated "art" vs. actual coaching diagram]*

The breakthrough came from separating understanding from rendering. Watch this:

```python
# What I type:
"2-1-2 forecheck with F1 pressuring puck carrier behind net, 
F2 covering strong side boards, F3 high slot, 
D1 and D2 at blue line"

# What the Hockey Diagram MCP understands:
{
    "players": [
        {"id": "F1", "position": {"x": 85, "y": 15}, "role": "forechecker"},
        {"id": "F2", "position": {"x": 70, "y": 35}, "role": "support"},
        {"id": "F3", "position": {"x": 50, "y": 50}, "role": "high_coverage"},
        {"id": "D1", "position": {"x": 35, "y": 25}, "role": "left_defense"},
        {"id": "D2", "position": {"x": 35, "y": 75}, "role": "right_defense"}
    ],
    "puck": {"x": 90, "y": 20},
    "movements": [
        {"from": "F1", "to": {"x": 90, "y": 20}, "type": "pressure"},
        {"from": "F2", "to": {"x": 75, "y": 10}, "type": "coverage"}
    ]
}

# What gets generated:
[Precise SVG diagram matching any coaching manual]
```

*[VIDEO PLACEHOLDER: Real-time diagram generation from natural language, showing the text input transforming into professional diagram]*

Last week's practice plan included 6 custom diagrams. Time to create them all: 8 minutes.

*[SCREENSHOT PLACEHOLDER: Practice plan PDF with embedded diagrams for station drills]*

## Problem #3: The Data Dilemma

Let me show you my Airtable setup for last Tuesday's practice:

*[SCREENSHOT PLACEHOLDER: Airtable view showing practice plan with linked drills, player attendance, and skill focus]*

**Practice Planning Table:**
```
Date: Nov 5, 2024
Theme: Defensive Zone Coverage
Duration: 60 minutes
Drills: [Linked to Drills table]
  - Corner Battle 2v2 (8 min)
  - D-Zone Coverage Walk-through (10 min)
  - 3v3 Small Area Game (12 min)
Players Present: 18/20
Skills Worked: [Tags: positioning, stick_checks, communication]
Notes: "Kids struggled with weak side coverage - need more reps"
```

**Player Development Tracking:**
```
Player: Liam M.
Position: Center
Recent Skills Practiced:
  - Faceoffs: ✓✓✓✓ (4 sessions)
  - Backchecking: ✓✓ (2 sessions)
  - Defensive positioning: ✓ (1 session) <- FLAG: Needs work
  
Next Focus Areas: [Auto-suggested based on gaps]
  - Defensive zone coverage
  - Weak side positioning
```

The magic moment came during our last game. Between periods, I pulled up:

```sql
-- Actual Airtable formula
FIND("breakout", {Drills.Description}) AND 
{Success_Rate} > 0.7 AND
{Complexity} = "Simple"

-- Returns: "D to D Behind Net" - 85% success rate in practice
```

We ran it. Three successful breakouts in the third period.

*[VIDEO PLACEHOLDER: Quick demo of filtering drills by success rate and pulling up video clips]*

## Problem #4: The Communication Cluster

Here's the actual n8n workflow I built, running right now:

*[SCREENSHOT PLACEHOLDER: n8n workflow canvas showing nodes and connections]*

**The Workflow Nodes:**
1. **Schedule Node** (runs daily at 5 AM)
2. **TeamSnap API Node**
   ```json
   {
     "endpoint": "/events",
     "team_id": "3847291",
     "days_ahead": 14
   }
   ```
3. **Data Transform Node**
   ```javascript
   // Clean up TeamSnap's... interesting... data structure
   events.map(event => ({
     title: event.name,
     date: formatDate(event.start_date),
     time: convert24to12(event.arrival_time),
     location: event.location_name,
     address: event.location_address,
     type: event.is_game ? "Game" : "Practice"
   }))
   ```
4. **OpenAI Node** (the clever bit)
   ```
   Prompt: "Add context for parents:
   - If game, add 'arrive 45 min early for warmup'
   - If tournament, add 'pack lunch and extra water'
   - If practice, note which group (skills vs scrimmage)"
   ```
5. **Notion API Node**
   ```json
   {
     "database_id": "8f3k2n5m9p1q",
     "properties": {
       "Title": "{{title}}",
       "Date": "{{date}}",
       "Tags": ["Schedule", "{{type}}"]
     }
   }
   ```

Last week, this workflow:
- Processed 12 schedule changes
- Added context to 8 events
- Saved me 2 hours of manual updates
- Resulted in zero "what time is practice?" texts

*[VIDEO PLACEHOLDER: n8n workflow executing in real-time, showing data transformation at each step]*

Parents now check one place:

*[SCREENSHOT PLACEHOLDER: Notion team page with embedded calendar, upcoming events, and team announcements]*

## Problem #5: The Engagement Equation

Here's an actual quiz interaction from yesterday:

*[SCREENSHOT PLACEHOLDER: Quiz app interface showing question, leaderboard, and hint system]*

**Question:** "In a 2-1-2 forecheck, where should F3 position themselves?"

**Tommy (age 9) answers:** "In front of the net"

**AI Response (not giving answer, but guiding):**
```
"Good thinking about net coverage, Tommy! 🏒 
But let's think about this together:
- If F1 is pressuring the puck carrier behind the net
- And F2 is covering the strong side boards
- And F3 is also down low by the net...

Who's watching the high slot? What happens if the other 
team makes a quick pass to their center at the blue line?"
```

**Tommy's second attempt:** "Oh! High slot to stop the breakout!"

**AI Response:** 
```
"Exactly! 🎯 You've got it! F3 stays high to:
1. Prevent easy breakout passes
2. Keep the puck in the zone
3. Be ready to rotate down if needed

You earned 10 points! You're now #3 on the leaderboard!"
```

Current quiz stats:
- **387 questions answered** this week
- **73% improvement** in systems knowledge
- **100% of kids** have used it at least once
- **"Can we do more hockey homework?"** - actual quote from a 9-year-old

*[VIDEO PLACEHOLDER: Kid using the app, showing the Socratic hint system in action]*

The prompt engineering for age-appropriate hints:

```python
system_prompt = """
You are a friendly youth hockey coach helping kids aged 8-10 
understand hockey concepts. 

Rules:
1. Never give the answer directly
2. Ask questions that lead to understanding
3. Use simple language (grade 3-4 level)
4. Reference situations they've seen in games
5. Celebrate when they figure it out
6. If stuck after 3 hints, provide answer with explanation

Keep responses under 50 words.
Use hockey emojis sparingly but effectively.
"""
```

## The Integration Magic

Here's where it gets beautiful. Watch what happens during a typical week:

**Monday Evening:**
```bash
> "Find me drills for defensive zone coverage for Wednesday's practice"
> MCP returns 5 appropriate drills
> "Generate diagrams for drills 2 and 4"
> Diagrams created and saved
```

**Tuesday Morning:**
```
> Airtable automation runs
> Emails drill plan to assistant coaches
> Links videos for pre-practice review
```

**Wednesday (Practice Day):**
```
> Check in players on Airtable mobile
> Run practice with printed diagrams
> Quick notes on what worked/didn't
```

**Thursday:**
```
> n8n workflow processes practice notes
> Updates player development tracking
> Suggests focus areas for next practice
> Publishes practice recap to Notion
```

**Friday:**
```
> Parents see updated team page
> Kids take quiz on defensive positioning
> AI tracks comprehension gaps
> I get data on what needs reinforcement
```

*[DIAGRAM PLACEHOLDER: System architecture showing all tools connected]*

## Real Impact, Real Numbers

Two months into the season:
- **Practice Planning:** 45 minutes → 8 minutes
- **Parent Communications:** 2 hours/week → 15 minutes
- **Drill Discovery:** Random browsing → Targeted search
- **Player Development Tracking:** Paper notes → Searchable database
- **System Comprehension (kids):** 40% → 73%
- **Parent Question Texts:** 15-20/week → 2-3/week
- **My Stress Level:** 📈 → 📉

## The Bigger Picture

Here's what two months of evening and weekend building taught me:

**These aren't hockey tools. They're patterns.**

Replace "hockey drill" with "sales playbook" or "onboarding process"
Replace "practice plan" with "project timeline" or "meeting agenda"  
Replace "player development" with "employee growth" or "skill matrices"
Replace "team parents" with "stakeholders" or "clients"

The volunteer coach problems are your enterprise problems, just with less ice and fewer zambonis.

## Your Turn

As I prepare for another 6 AM practice (this time with a complete plan generated in 5 minutes, diagrams included, parents notified, and kids already studying the systems on their quiz app), I'm thinking about you reading this:

**What knowledge is trapped in your organization's PDFs?**
**What diagrams are drawn and redrawn on whiteboards?**
**What data lives in spreadsheets that no one opens?**
**What updates are you manually copying between systems?**
**What learning could be gamified for engagement?**

The gap between idea and implementation has never been smaller. These tools took evenings and weekends to build, not months and budgets.

Start small. Solve something real. Let AI amplify your expertise.

---

*Next week, I'll share the complete video tutorials and starter code for building your own MCP servers. The game is changing. The question isn't whether AI will transform how we work—it's whether we'll be the ones guiding that transformation.*

*Keep coaching the machine,*
*Stewart

P.S. - Last night, Liam's team executed a perfect 2-1-2 forecheck. F3 stayed high in the slot, just like the quiz taught them. The other team's coach asked me afterward, "How do nine-year-olds know positioning that well?" 

I showed him the quiz app. He wants the link.

The future isn't about replacing coaches—it's about giving every coach the tools to be their best.