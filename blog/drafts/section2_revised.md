## Problem #1: The Knowledge Maze

Hockey has gotten expensive. Really expensive. We're talking $5,000 to $15,000 per season per kid in competitive leagues. Part of that cost? Access to elite coaching knowledge. The best power skating instructors, skills coaches, and tactical experts—they're incredible, but not every family can afford them.

Meanwhile, there's amazing hockey knowledge freely available—it's just impossible to find when you need it.

Here's what my October 24th practice planning looked like:

**9:15 PM:** Open Hockey Canada PDF (247 pages)  
**9:18 PM:** Search for "passing" - 73 results  
**9:22 PM:** Find a drill that might work, but it's for U14  
**9:30 PM:** Search YouTube - 2 hours of videos to find 5 useful minutes
**9:45 PM:** Give up, draw something from memory

The knowledge exists. Hockey Canada, USA Hockey, the OMHA—they've published thousands of drills, progressions, and systems. It's all there, free, created by expert coaches. But it's trapped in PDFs, scattered across websites, buried in hour-long YouTube videos.

So I built something different. Not another API, but an MCP server designed for how AI actually needs information:

```bash
$ claude "Find me passing drills for 9-year-olds that work on timing"

Claude: I'll search the hockey knowledge base for age-appropriate passing drills 
focusing on timing...

Found 12 relevant drills. Here's the best match:

PASSING – GIVE AND GO TIMING
- Age: U10 (perfect for 9-year-olds)
- Focus: Timing of return pass, reading defender
- Setup: Simple - uses 1/4 ice, 6 players
- Key teaching point: "Pass and accelerate - the pass back 
  comes to where you're going, not where you were"
- Common mistake: Kids wait for return pass instead of driving
- You last ran this: October 15 (9 days ago)
- Success rate when you ran it: 75%

[Shows diagram]

Want me to find complementary drills or see the progression?
```

*[VIDEO PLACEHOLDER: Natural conversation with Claude finding and explaining drills]*

This isn't just an API wrapper. MCP servers are built for AI—they provide context, understand coaching flow, and bring domain intelligence. A traditional API returns data. An MCP server understands that if I'm looking for passing drills, I probably need to know equipment, ice requirements, and what to watch for when kids struggle.

**Building the Knowledge Base:**

I didn't create this content—I liberated it. Using Claude Code, I:
1. Downloaded public coaching manuals (with attribution maintained)
2. Scraped coaching websites like IceHockeySystemsInc.com and HockeyShare.com
3. Parsed 4,000+ pages of PDFs  
4. Extracted, structured, and cleaned drill descriptions for LLM use
5. Indexed 100+ hours of YouTube coaching videos (transcripts and key moments)
6. Enriched everything with metadata: age levels, skill focus, complexity ratings

The knowledge base now contains:
- **1,247 drills** from Hockey Canada, USA Hockey, OMHA, and coaching sites (all attributed)
- **89 complete practice themes** with learning objectives
- **156 skill progressions** following the LTAD framework
- **43 team systems** broken down by age appropriateness

*All sources are credited. This is about making publicly available coaching education accessible, not replacing it.*

**The MCP Advantage:**

While I'm showing Claude examples here, these MCP tools work with any client that supports the protocol—which is growing fast. You can use them with:
- Claude (Desktop, Code, or API)
- Cline
- Zed
- Sourcegraph Cody
- Or build your own client

The beauty of MCP is it's not locked to one AI provider. Build once, use everywhere.

**What This Enables:**

The MCP server doesn't create practice plans for me—coaching is still collaborative, still human. But now I can:

- **Create practice plans** grounded in proven progressions
- **Build team playbooks** kids can actually understand
- **Design game-day strategies** based on what we've practiced successfully
- **Develop apps** (like the quiz) backed by real hockey knowledge

Last Tuesday, I built our team's defensive zone coverage playbook in 20 minutes. It would have taken me a weekend of research before. More importantly, it's based on Hockey Canada's actual teaching progression, not my half-remembered junior hockey experience.

*For my business leader friends: How much expertise in your organization is trapped the same way? Not secret, just inaccessible. The pattern—and solution—is identical.*

This doesn't replace expert coaches. You still need someone who's seen a thousand kids learn to skate backwards, who knows when to push and when to encourage. But it democratizes the foundational knowledge. Every volunteer coach can access the same drills the pros use.

Because at the end of the day, we're all just trying to help kids love the game.