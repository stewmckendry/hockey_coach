# From the Rink to the Terminal: How AI Helped Me Coach Smarter, Not Harder

It's 9 PM on a Thursday, October 26th. Tomorrow's practice is at 6 AM. I'm staring at a blank practice plan, knowing I need drills for 20 nine-year-olds at different skill levels, an email update for parents about the weekend tournament, and somehow need to make it all fun while teaching proper defensive zone coverage. 

Welcome to volunteer coaching in competitive youth hockey.

Let me be clear—I don't coach because I have to. Like the other moms and dads standing in cold rinks at ungodly hours, I coach because it's an amazing privilege to spend this time with our kids. This summer, I was on the diamond as assistant coach when Liam's baseball team made it to provincials. Watching these kids grow, compete, and become best friends? That's the real payment.

But the administrative side of coaching? That's what steals time from actually coaching.

If you've been following Coaching the Machine, you know I took the summer off from writing. But I never stopped building. While enjoying those baseball games, I was quietly assembling a suite of AI tools for Liam's upcoming hockey season—his first year playing 'A' level in the GTHL.

What started as a simple question—"Can AI help me be a better volunteer coach?"—turned into something much more interesting. And applicable far beyond the rink.

## The Game Changer: Claude Code

Before summer, I was using OpenAI Codex in the browser—which was already better than ChatGPT since it could connect to my repo. But Claude Code? This is next level. It's not just coding assistance; it's automated app delivery.

The difference hit me when I needed to build a quiz app for the kids to learn hockey systems. Here's what happened:

```bash
$ claude "Create a hockey IQ quiz app where kids can learn positioning through questions"

Claude: I'll help you build a complete quiz application. Let me plan this properly first.

[Enters plan mode]
## Architecture:
- Next.js app with TypeScript
- OpenAI for Socratic hints
- Leaderboard with Supabase
- Mobile-responsive design

Creating GitHub issues for tracking:
✓ Issue #47: Quiz question engine
✓ Issue #48: Socratic hint system  
✓ Issue #49: Leaderboard implementation
✓ Issue #50: Parent dashboard

Now implementing with test-driven development...
```

Twenty minutes later, I had a working app. Not a prototype—a deployed app that kids were using that night.

**The key differentiators:**

**MCP Servers** - These are game-changers. Need web search? Add `exa`. Documentation lookup? Add `ref-tools`. Want to crawl TeamSnap for schedules? Build your own. These become Claude's superpowers, not just yours.

**Plan Mode** - Not "vibe coding" but proper software architecture. Claude breaks down complex builds into Issues, tracks them, implements systematically. Like having a technical lead and senior dev in one.

**Parallel Development** - "Launch a subagent to build the API while we work on the UI." Multiple Claude sessions working on different parts, all aware of each other through the shared codebase.

**Visual Iteration** - "Use Playwright to screenshot the app and suggest improvements." Claude sees what users see, not just code.

**Voice Mode** - Walking between rinks, I describe features verbally. Claude writes the specs. Implementation starts before I'm home.

The terminal might seem intimidating, but it's just a conversation. And that conversation can build production apps in the time it used to take to set up a development environment.

*[VIDEO PLACEHOLDER: 3-minute demo showing quiz app creation from concept to deployment]*

This isn't about replacing developers—it's about amplifying builders. Every volunteer coach, every side-project parent, every person with a problem to solve can now build the solution.

*[SCREENSHOT PLACEHOLDER: Claude Code terminal showing Issues created, tests passing, app deployed]*