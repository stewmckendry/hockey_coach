# From the Rink to the Terminal: How AI Helped Me Coach Smarter, Not Harder

It's 9 PM on a Thursday, October 26th. Tomorrow's practice is at 6 AM. I'm staring at a blank practice plan, knowing I need drills for 20 nine-year-olds at different skill levels, an email update for parents about the weekend tournament, and somehow need to make it all fun while teaching proper defensive zone coverage. 

Welcome to volunteer coaching in competitive youth hockey.

If you've been following Coaching the Machine, you know I took the summer off from writing. But I never stopped building. While my son Liam and his teammates were making memories at baseball provincials, I was quietly assembling a suite of AI tools for his upcoming hockey season—his first year playing 'A' level in the GTHL.

What started as a simple question—"Can AI help me be a better volunteer coach?"—turned into something much more interesting. And applicable far beyond the rink.

## The Game Changer: Claude Code

First, let me share the biggest unlock of the past few months: I switched my development environment to Claude Code. If you haven't tried it yet, imagine having a senior developer who can see your entire codebase, understands context across files, and helps you build through conversation.

Here's what changed everything: I could describe what I wanted in plain English and watch it come to life. Not generate-and-pray like with ChatGPT. Real collaboration where Claude could see my files, understand my architecture, and build with me.

```bash
$ claude "I need to search my hockey drill database. Can you help create an MCP tool for this?"

Claude: I can see you have a ChromaDB setup with hockey drills. Let me create an MCP server 
that provides searchable access. First, let me check your existing structure...

[Claude reads files, understands schema, writes working code]

$ python servers/hockey_mcp.py
> MCP Server running on port 8000
> Collections loaded: drills (1247), tactics (156), skills (89)
```

*[VIDEO PLACEHOLDER: 2-minute demo showing Claude Code helping build a search function, with terminal commands and real-time file editing]*

Why this matters: In one evening, I went from idea to working implementation. More importantly, when it didn't work perfectly the first time (spoiler: it never does), Claude could see the error, understand the context, and fix it with me. This isn't about replacing developers—it's about amplifying what one motivated person can build.

*[SCREENSHOT PLACEHOLDER: Claude Code terminal showing the conversation flow and generated code side-by-side]*

## Problem #1: The Knowledge Maze

Every new coach faces the same challenge. There's incredible hockey knowledge out there—scattered across PDFs, websites, YouTube videos, and the minds of experienced coaches. But when you need it, you can't find it.

Let me show you exactly what I mean. Here's what my October 24th practice planning looked like before:

**9:15 PM:** Open Hockey Canada PDF (247 pages)  
**9:18 PM:** Search for "passing" - 73 results  
**9:22 PM:** Find a drill that might work, but it's for U14  
**9:25 PM:** Open bookmark folder "Hockey Drills" - 47 saved links  
**9:28 PM:** Click through three broken links  
**9:31 PM:** Find a decent drill but no idea if we ran it last week  
**9:45 PM:** Give up, draw something from memory

Here's what happened this Tuesday:

```bash
# Using the Hockey Knowledge MCP tool
$ mcp-cli hockey search-drills \
  --query "passing drills for U10 that work on give-and-go in neutral zone" \
  --age "U10" \
  --skills "passing,timing" \
  --complexity "medium"

# Returns in 0.3 seconds:
{
  "drill": "PASSING – PASS AND MOVE #3",
  "source": "Hockey Canada Skills Manual p.47",
  "equipment": "6 pucks, 2 nets, 6 cones",
  "setup": "Players in opposite corners, coach at center ice",
  "teaching_points": [
    "Tape-to-tape passes",
    "Present stick as target", 
    "Quick feet after pass"
  ],
  "progression": [
    "Start stationary",
    "Add movement",
    "Add passive defender",
    "Full pressure"
  ],
  "common_mistakes": "Players standing still after passing",
  "diagram_url": "generated_diagram_123.svg",
  "last_used": "2024-10-15 (9 days ago)"
}
```

*[VIDEO PLACEHOLDER: Live search showing natural language query returning specific drills with teaching points]*

The knowledge base now contains:
- **1,247 drills** from Hockey Canada, USA Hockey, OMHA manuals
- **89 complete practice plans** organized by theme and age
- **156 skill progressions** mapped to LTAD framework
- **43 team systems** with age-appropriate variations

But here's what I learned the hard way: Having data isn't enough. The first version returned drills, but coaches think in practice flows, not individual drills. So we evolved it:

```bash
$ mcp-cli hockey create-practice \
  --theme "defensive zone coverage" \
  --duration 60 \
  --age "U10" \
  --skill-focus "positioning"

# Returns complete practice plan with:
- Warm-up (8 min): "Russian Circles with Puck"
- Skill stations (20 min): 2 drills, diagrams included
- Team tactics (20 min): "Box+1 Introduction"  
- Scrimmage focus (10 min): "Defensive side positioning"
- Cool-down (2 min): "Shootout fun"
```

*For my business leader friends: Your organization has this same problem. Knowledge trapped in SharePoint, Confluence, PDFs that no one can find when they need it. The pattern is the same.*

## Problem #2: The Whiteboard Translation

The hockey whiteboard is iconic. Every coach has stood at one, drawing X's and O's, arrows everywhere. But here's what I discovered: asking AI to generate hockey diagrams produces abstract art, not coaching tools.

My first attempts were... humbling:

```
Me: "Draw a 2-1-2 forecheck diagram"

ChatGPT: 
     O
    / \
   O   O
  O     O
[This is supposed to be a hockey rink?]

Me: "Generate an image of a 2-1-2 forecheck"

DALL-E: [Creates beautiful artwork featuring tiny stick figures 
on what might be ice, or possibly a blue carpet]
```

*[IMAGE PLACEHOLDER: Side-by-side comparison of AI-generated "art" vs. actual coaching diagram]*

The breakthrough wasn't better AI—it was combining AI understanding with programmatic precision. Watch this transformation:

```bash
$ mcp-cli hockey-diagram create \
  --description "2-1-2 forecheck with F1 pressuring puck carrier behind net, 
                 F2 covering strong side boards, F3 high slot, 
                 D1 and D2 holding blue line"

# Step 1: AI understands the description
Analyzing: "2-1-2 forecheck" → Formation identified
Processing: "F1 pressuring behind net" → Position: (85, 15)
Processing: "F2 strong side boards" → Position: (70, 35)

# Step 2: Validates against hockey rules
✓ All 5 skaters positioned
✓ Formation matches 2-1-2 structure
✓ Positions are tactically sound

# Step 3: Generates precise SVG
{
  "players": [
    {"id": "F1", "position": {"x": 85, "y": 15}, "role": "forechecker"},
    {"id": "F2", "position": {"x": 70, "y": 35}, "role": "support"},
    {"id": "F3", "position": {"x": 50, "y": 50}, "role": "high_coverage"},
    {"id": "D1", "position": {"x": 35, "y": 25}, "role": "left_defense"},
    {"id": "D2", "position": {"x": 35, "y": 75}, "role": "right_defense"}
  ],
  "movements": [
    {"from": "F1", "to": {"x": 90, "y": 20}, "type": "forecheck_pressure"},
    {"from": "F2", "to": {"x": 75, "y": 10}, "type": "seal_boards"}
  ]
}

Output: professional_diagram.svg ✓
```

*[VIDEO PLACEHOLDER: Real-time diagram generation from natural language, showing the text input transforming into professional diagram]*

Last week's practice included 6 custom diagrams. Time to create: 8 minutes.  
Previous method (PowerPoint + screenshots): 45 minutes minimum.

*[SCREENSHOT PLACEHOLDER: Practice plan PDF with embedded diagrams for station drills]*

## Problem #3: The Data Dilemma

Coaching isn't just running drills. It's tracking development, identifying patterns, and making adjustments. Most volunteer coaches use nothing, a notebook, or if they're fancy, a spreadsheet that becomes a mess by November.

Enter Airtable—but not just as a database. As an intelligent coaching assistant.

Here's my actual setup from our October 31st practice:

*[SCREENSHOT PLACEHOLDER: Airtable view showing practice plan with linked drills, player attendance, and skill focus]*

**Practice Planning Table:**
```
Date: October 31, 2024
Theme: Defensive Zone Coverage
Duration: 60 minutes
Conditions: Half-ice available (sharing with U11)

Drills: [Linked records]
  ✓ Corner Battle 2v2 (8 min) - Success: 85%
  ✓ D-Zone Coverage Walk-through (10 min) - Success: 60%
  ⚠ 3v3 Small Area Game (12 min) - Success: 45%
  
Players Present: 18/20 (Bobby: sick, Emma: tournament)
Skills Worked: [positioning, stick_checks, communication]

Post-Practice Notes: 
"Weak side coverage still confusion. Kids collapsing to net. 
Need more reps with 'stay on your check' concept"

Auto-generated insights:
- Low success rate on 3v3 suggests complexity too high
- Consider prerequisite drill for spatial awareness
- 6 players haven't practiced weak-side positioning in 2 weeks
```

**Player Development Tracking (Actual data, name changed):**
```
Player: Jackson M. (#17)
Position: Center
Season Stats: 4G, 7A in 8 games

Skills Progression:
  Faceoffs:           ████░ (4 of 5 sessions)
  Backchecking:       ██░░░ (2 of 5 sessions) ⚠️
  Defensive coverage: █░░░░ (1 of 5 sessions) 🚨
  Passing:            █████ (5 of 5 sessions) ✓
  
AI-Suggested Focus: 
"Jackson shows strong offensive instincts but needs defensive reps. 
Consider pairing with defensive-minded winger for next scrimmage."

Parent Report Auto-generated:
"Jackson is developing well offensively! We're focusing on 
defensive positioning to round out his game."
```

The magic moment: During our game on November 2nd, between periods I checked:

```sql
-- Quick Airtable query during intermission
SELECT drill_name, success_rate 
FROM practice_drills 
WHERE tag CONTAINS 'breakout' 
  AND success_rate > 70
  AND complexity = 'Simple'
ORDER BY last_used DESC

-- Result: "D-to-D Behind Net" - 85% success rate
-- Last used: 3 days ago, kids should remember it
```

We ran it. Three successful breakouts in the third period. Data-driven coaching in real-time.

*[VIDEO PLACEHOLDER: Quick demo of filtering drills by success rate during a game]*

## Problem #4: The Communication Cluster

"When's our next game?"
"What time is practice?"  
"Where's the tournament schedule?"
"Do we need to bring both jerseys?"

If you coach, you know these texts. They come at all hours, usually when the information is buried in TeamSnap, or worse, in an email chain from three weeks ago.

I wanted our families to have one source of truth—a Notion team site. But manually copying from TeamSnap to Notion? That's a hard no.

This is where n8n became the unexpected hero. Here's the actual workflow that runs every morning at 5 AM:

*[SCREENSHOT PLACEHOLDER: n8n workflow canvas showing nodes and connections]*

**The Workflow That Saved My Sanity:**

1. **Schedule Trigger** (5:00 AM daily)
```javascript
// Node: Cron trigger
schedule: '0 5 * * *'  // Every day at 5 AM
```

2. **TeamSnap API** 
```javascript
// Node: HTTP Request
const options = {
  url: 'https://api.teamsnap.com/v3/events',
  headers: { 'Authorization': 'Bearer [REDACTED]' },
  params: {
    team_id: '[REDACTED]',
    days_ahead: 14
  }
}
// Returns: Raw event data (messy)
```

3. **Data Transformation**
```javascript
// Node: Code - Clean up TeamSnap's data structure
const cleaned = $input.all().map(event => ({
  title: event.json.name,
  date: DateTime.fromISO(event.json.start_date).toFormat('MMM dd'),
  time: event.json.is_game 
    ? `Arrive: ${event.json.arrival_time}` 
    : `On-ice: ${event.json.start_time}`,
  location: event.json.location?.name || 'Home rink',
  type: event.json.is_game ? 'Game' : 'Practice',
  opponent: event.json.opponent?.name || null
}));

return cleaned;
```

4. **AI Enhancement** (The clever bit)
```javascript
// Node: OpenAI
prompt: `Add helpful context for hockey parents:
Event: {{title}} at {{time}}
Type: {{type}}

Add relevant reminders like:
- Games: arrival time, both jerseys?, water bottles
- Practice: specific gear needed, pickup time
- Tournaments: pack lunch, cash for admission
Keep it brief and parent-friendly.`

// Returns: Enhanced event with context
```

5. **Notion Update**
```javascript
// Node: Notion API
{
  "parent": { "database_id": "[REDACTED]" },
  "properties": {
    "Title": { "title": [{ "text": { "content": "{{title}}" }}]},
    "Date": { "date": { "start": "{{date}}" }},
    "Type": { "select": { "name": "{{type}}" }},
    "Details": { "rich_text": [{ "text": { "content": "{{ai_context}}" }}]},
    "Last_Updated": { "date": { "start": "{{now}}" }}
  }
}
```

Last week's metrics:
- **12 schedule changes** processed automatically
- **8 events** enhanced with helpful context  
- **2 hours** saved on manual updates
- **Zero** "what time is practice?" texts (down from 15-20)
- **One** grateful team manager (my wife)

*[VIDEO PLACEHOLDER: n8n workflow executing in real-time, showing data transformation at each step]*

Parents now have one beautiful, always-updated page:

*[SCREENSHOT PLACEHOLDER: Notion team page with embedded calendar, upcoming events, and team announcements]*

## Problem #5: The Engagement Equation

Hockey kids are competitive about everything. So when I needed them to learn systems and positioning, I knew worksheets wouldn't work. Enter the Hockey IQ Quiz—but with a twist.

Here's an actual interaction from November 3rd:

*[SCREENSHOT PLACEHOLDER: Quiz app interface showing question, leaderboard, and hint system]*

**Question:** "In a 2-1-2 forecheck, where should F3 position themselves?"

**Ethan (age 9) answers:** "In front of the net"

**AI Response (not giving answer, but guiding):**
```
"Good thinking about net coverage, Ethan! 🏒 
But let's think about this together:
- If F1 is pressuring behind the net
- And F2 is on the boards
- And F3 is also down low...

Who's watching the middle of the ice? What happens 
if they pass to their center?"
```

**Ethan's second attempt:** "Oh! High slot to stop the breakout!"

**AI Response:** 
```
"EXACTLY! 🎯 You've got it! F3 stays high to:
1. Stop breakout passes
2. Keep puck in zone
3. Support if puck goes to corner

You earned 10 points! You're now #3 on the leaderboard!"
```

The Socratic method, powered by AI:

```python
# Actual prompt engineering for age-appropriate hints
system_prompt = """
You are a friendly youth hockey coach helping kids aged 8-10 
understand hockey concepts. 

Rules:
1. Never give the answer directly on first attempt
2. Ask questions that lead to understanding  
3. Use grade 3-4 vocabulary
4. Reference game situations they've experienced
5. Celebrate when they get it right
6. After 3 attempts, provide answer with simple explanation

Keep responses under 50 words.
Use hockey emojis sparingly (max 2 per response).
Sound encouraging, not frustrating.
"""
```

Current stats from our team:
- **387 questions answered** this week (avg 19 per kid)
- **73% improvement** in systems knowledge test
- **18 of 20 kids** have used it (2 don't have devices)
- **"Can we do more hockey homework?"** - actual quote from Lucas, age 9
- **3 parents** asked if there's an adult version

*[VIDEO PLACEHOLDER: Kid using the app, showing the Socratic hint system in action]*

## The Integration Magic: A Week in the Life

Here's where individual tools become an ecosystem. Let me walk you through last week:

**Sunday Evening (Nov 3, 8:30 PM):**
```bash
$ mcp-cli hockey suggest-practice \
  --based-on "last_game_stats" \
  --focus "weak_areas"

Suggestion: "Focus on defensive zone coverage. 
Team gave up 4 goals on lost coverage in last game."

$ mcp-cli hockey create-practice \
  --theme "defensive zone coverage" \
  --duration 60

Practice plan created with 5 drills, 3 diagrams generated
```

**Monday Morning (Nov 4, 5:00 AM):**
```
> n8n workflow runs automatically
> Fetches TeamSnap updates  
> Notices Thursday game moved to 7 PM
> Updates Notion with alert flag
> Sends notification to parent WhatsApp group
```

**Tuesday (Nov 5, Practice Day):**
- 5:45 AM: Check Airtable on phone, review plan
- 6:00 AM: Practice starts, QR code for diagrams  
- 6:50 AM: Quick notes in Airtable: "Kids struggled with weak-side"
- 10:00 AM: AI processes notes, suggests follow-up drills

**Wednesday (Nov 6):**
```javascript
// Automated Airtable → Quiz generation
if (practice.notes.contains("struggled")) {
  generate_quiz_questions(topic: practice.struggle_area)
  notify_players("New quiz available! Learn about weak-side coverage")
}
```
- Result: 14 kids complete quiz that evening
- Average score: 82% (up from 45% previous week)

**Thursday (Nov 7, Game Day):**
- Pre-game: Check Airtable for successful breakout plays
- Period 2: Down 2-1, implement "D-to-D Behind Net" 
- Result: 2 successful breakouts, tie game 2-2
- Post-game: Record what worked in Airtable

**Friday (Nov 8):**
- Parents check Notion: See game recap, next week schedule
- Kids check quiz app: New questions based on game situations
- I check metrics: 15 minutes total admin time this week

*[DIAGRAM PLACEHOLDER: System architecture showing all tools connected with data flow]*

## Real Impact, Real Numbers

Two months into the season, here's what changed:

**Time Saved:**
- Practice Planning: 45 min → 8 min (82% reduction)
- Parent Communications: 2 hrs/week → 15 min (87% reduction)  
- Game Preparation: 30 min → 5 min (83% reduction)
- Admin Tasks: 3 hrs/week → 30 min (83% reduction)

**Quality Improved:**
- Practice Variety: 3-4 drills repeated → 47 unique drills used
- Player Development Tracking: "Some notes" → Every skill tracked
- Parent Satisfaction: "When's practice?" texts down 92%
- Kid Engagement: 1 kid asking about systems → 18 kids doing "homework"

**Hockey Improved:**
- Systems Knowledge: ~40% test scores → 73% average
- Breakout Success: 35% → 58% success rate
- Defensive Coverage: 6 goals against/game → 3.5 goals against
- Fun Factor: "Practice is boring" → "Can we stay longer?"

## The Failure That Led to Success

Let me be honest—this didn't all work perfectly. My first attempt at the quiz app was a disaster. I made it too complex, like a hockey SAT. Kids logged in once and never came back.

The diagram tool initially created beautiful, useless art. The MCP server crashed constantly until I learned about connection pooling. The n8n workflow sent 47 notifications at 3 AM once (parents were... not happy).

But here's what I learned: Every failure taught me what coaches and parents actually need. Not perfect tools, but practical ones. Not complex systems, but simple solutions to real problems.

Claude Code made iteration fast. Fail, fix, try again—all in one evening instead of weeks.

## The Bigger Picture: It's Not About Hockey

These aren't hockey tools. They're patterns that apply everywhere:

**Knowledge Management:**
- Replace "hockey drills" → "sales playbooks" or "SOPs"
- Replace "practice plans" → "project templates" or "training modules"

**Visual Communication:**
- Replace "hockey diagrams" → "network architectures" or "process flows"  
- Replace "play systems" → "workflow diagrams" or "org charts"

**Data Tracking:**
- Replace "player development" → "employee skills matrix"
- Replace "practice success rates" → "project KPIs"

**System Integration:**  
- Replace "TeamSnap→Notion" → "Salesforce→Slack" or "Jira→Teams"
- Replace "parent updates" → "stakeholder reports"

**Engagement Through Gamification:**
- Replace "hockey quiz" → "compliance training" or "onboarding"
- Replace "leaderboard" → "performance dashboards"

The volunteer coach problems are your enterprise problems, just with less ice and fewer zambonis.

## Your Turn: From Idea to Implementation

As I prepare for tomorrow's 6 AM practice (plan done, diagrams ready, parents notified, kids studying positioning), I'm thinking about you:

**What knowledge is trapped in your organization?**  
Not in a database, but in PDFs no one opens?

**What processes are drawn on whiteboards daily?**  
Then photographed, then lost?

**What data lives in spreadsheets?**  
That could be driving decisions?

**What systems don't talk to each other?**  
Requiring manual copy-paste?

**What learning could be engaging?**  
Instead of mandatory and ignored?

The gap between idea and implementation has never been smaller. These tools took evenings and weekends, not months and budgets. The barrier isn't technical—it's starting.

## How to Access These Tools

Want to try these yourself? Here's how:

**GitHub Repository:** [github.com/stewmckendry/thunder-playbook](https://github.com/stewmckendry/thunder-playbook)  
(Note: Sanitized for privacy, but fully functional)

**Key Components:**
- Hockey MCP Server: `servers/hockey_mcp.py`
- Diagram Generator: `hockey_diagram_mcp/`  
- Quiz App: `web_app/`
- n8n Workflows: `workflows/` (JSON exports)

**Getting Started:**
1. Clone the repo
2. Set up your virtual environment  
3. Add your API keys (.env file)
4. Run `python start_services.py`
5. Start building your own version

**Required Services:**
- Claude Code (for development)
- ChromaDB (vector database)
- Airtable (free tier works)
- n8n (self-hosted or cloud)
- Notion API access

---

*Next week, I'll share video tutorials walking through each tool build, plus templates you can adapt for your own use cases. The game is changing. The question isn't whether AI will transform how we work—it's whether we'll be the ones guiding that transformation.*

*Keep coaching the machine,*  
*Stewart*

P.S. - Saturday's game: Liam's team executed the 2-1-2 forecheck perfectly. F3 stayed high, just like the quiz taught them. We won 4-2. The other coach asked afterward, "How do nine-year-olds know positioning that well?" 

I showed him the quiz app. He's already set up his own version.

The future isn't about AI replacing coaches—it's about giving every coach, every leader, every builder the tools to be their best.

Want to see it in action? Check out the demo videos linked throughout this post, or better yet, join me for a live walkthrough next Thursday at 8 PM EST (after practice, of course).