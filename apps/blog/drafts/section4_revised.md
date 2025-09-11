## Problem #3: The Data Dilemma

Coaching isn't just running drills. It's tracking what works, identifying patterns, and making adjustments. Most volunteer coaches use nothing, a notebook, or if they're fancy, a spreadsheet that becomes a mess by November.

The result? We're mostly making it up as we go.

Enter Airtable—but not just as a database. As an intelligent coaching assistant that adds evidence to intuition.

Here's my actual setup from our October 31st practice:

*[SCREENSHOT PLACEHOLDER: Airtable view showing practice plan with linked drills, attendance, and success tracking]*

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
"Weak side coverage still confusion. Kids collapsing to net instead 
of staying on their check. The 3v3 game was chaos - too complex for 
where they are. Need to go back to 2v2 and build up. Also, kids 
are tired by station 3 - maybe flip order next time."

Key Insights for Next Practice:
- Start with 2v2 defensive coverage, build to 3v3
- Energy management: put complex drills earlier
- 6 kids still don't understand "stay on your check" concept
```

**The MCP Integration**

Here's the beautiful part—I'm not manually entering this data. Using the Airtable MCP tool in Claude Code:

```bash
$ claude "Update today's practice in Airtable. 3v3 drill didn't work well."

Claude: I'll update your practice record and add notes about the 3v3 drill.
Let me find today's practice first...

Found: October 31st practice - Defensive Zone Coverage

Updating drill success rates:
- Corner Battle 2v2: 85% (worked well)
- 3v3 Small Area Game: 45% (too complex)

Added note: "3v3 was chaos - kids not ready for this complexity.
Back to 2v2 foundation work needed."

Want me to suggest similar drills that might work better?
```

Setup, create records, read records—all through conversation with Claude Code (or any MCP-supported app like Cline, Zed, etc.). No switching between applications, no manual data entry.

**What Actually Gets Tracked:**
- Which drills worked (success rate based on observation)
- What didn't work and why (detailed notes)
- Energy levels throughout practice
- Which concepts kids struggle with
- Ice conditions, attendance, equipment issues

**What It Enables:**

Pre-practice planning:
```bash
$ claude "What breakout drills worked best for our team?"

Claude: Based on your Airtable data, here are your most successful breakout drills:
1. "D-to-D Behind Net" - 85% success rate (practiced 4 times)
2. "Simple Wheel" - 78% success rate (practiced 3 times)
3. "Up the Boards" - 72% success rate (practiced 5 times)

Your notes say the team struggles with complex outlet passes,
so I'd recommend starting with "D-to-D Behind Net."
```

**The Plan: Adding Game Stats**

Next phase is tracking what happens in games:
- Goals allowed by zone (defensive, neutral, offensive)
- Successful breakouts vs attempts  
- Power play effectiveness
- Which systems worked against which opponents

Not to create pressure on kids, but to understand what we're teaching versus what's working in real situations.

*[VIDEO PLACEHOLDER: Demo of updating practice notes through Claude conversation]*

**The Real Impact:**

Before: "I think we worked on passing last week..."
Now: "We've run 12 passing drills this month, here are the 3 most successful ones."

Before: "The kids seem to struggle with..."  
Now: "Based on 8 practices, here are the specific concepts that need work."

Before: "Let's try this system..."
Now: "This breakout worked 85% of the time in practice, let's use it."

Evidence over intuition. Data-informed coaching instead of making it up as we go.

*For my business friends: How many of your team meetings, training sessions, or process improvements are based on "I think this worked" versus actual data? Same opportunity.*