# From the Rink to the Terminal: How AI Helped Me Coach Smarter, Not Harder

Welcome back to Coaching the Machine, where we explore how humans and AI can build together. I took the summer off from writing, enjoying endless hours at ball diamonds watching Liam's team make their run to provincials. But the AI landscape doesn't pause—GPT-5 speculation heated up, agents became the next frontier, and MCP servers flooded in as every product company jumped on the bandwagon.

This explosion of new tools presented the perfect opportunity to experiment. I had two goals: First, stretch beyond my OpenAI comfort zone to discover what toolkit would give me the most frictionless AI experience. Second, apply these tools to something I'm passionate about—coaching hockey. With Liam moving from Select to 'A' level in the GTHL, I needed to up my game too.

The challenge was clear: less admin time (volunteer coaching is a side-of-desk job), better content and experience to match the higher level of play, and more actual teaching moments with the kids instead of searching through PDFs at 11 PM. What follows is how I used Claude Code, MCP servers, and visual automation to transform coaching from an administrative burden into what it should be—time on ice helping kids love the game.

## The Game Changer: Claude Code

Before summer, I was using OpenAI Codex in the browser—which was already better than ChatGPT since it could connect to my repo. But Claude Code completely changed my development experience. For those unfamiliar, Claude Code is Anthropic's CLI tool that runs in your terminal, letting you have a conversation with Claude while it directly reads and writes files in your codebase. It felt like working with a senior developer who never gets tired and has access to every tool I need.

Yes, the terminal interface isn't everyone's cup of tea—I get it. But you quickly forget about that when you see how frictionless it makes building. No more copy-pasting code between browser and editor, no more losing context when switching tabs. 

**What makes Claude Code different (and yes, there are alternatives like OpenAI's CLI and Google's Gemini CLI):**

**Direct file access** - Claude works right in your terminal with full access to your codebase. No copy-paste, no context loss. It reads your files, understands your project structure, and writes code directly where it needs to go.

**MCP Servers (Model Context Protocol)** - Think of these as apps for AI. They're being released like an app store, and each one gives Claude new capabilities. Need research? Add Exa. Managing repos? GitHub MCP. Database work? Airtable. Content management? Notion, Confluence, or Jira. Security scanning? Semgrep. UI testing? Playwright. It's a Swiss Army knife of tools that connect Claude to all your systems—incredibly powerful for real development work.

**SDLC best practices built in** - You can encode your development workflow right into Claude. Use `/plan` for proper architecture design, spawn parallel agents with git worktrees for isolated development, enforce test-driven development, or even use `/learning-mode` where Claude teaches you instead of doing everything for you. It's human-led, AI-assisted development at its best.

**Watch this 2-minute demo to see it in action:**

*I ask Claude to build a system that turns game stats into AI-generated stories for our team's Notion site. Watch as Claude uses MCP tools to create an Airtable database, build an n8n workflow connecting to OpenAI, and deploy everything—turning 63 minutes of real development into a 2-minute showcase. Yes, there was debugging. Yes, it took iterations. That's real development.*

[Video: Claude Code building game recap automation with MCP tools]

## The Knowledge Liberation

Hockey is the best sport on earth (I'm biased—yes, baseball's up there too). The game is amazing from pros to youth, and the people—coaches, instructors, organizations—are incredible. There's a huge body of resources out there. Hockey Canada, USA Hockey, the OMHA, countless third parties—everything's been written down, filmed, documented. But it's trapped in 250-page PDFs, scattered across websites, buried in hundreds of YouTube videos. For a mom or dad trying to build a great practice on a Tuesday evening, there's no time to find this stuff, let alone read it. So we end up drawing from memory or paying for specialist instruction.

What if you had a database of hockey knowledge at your fingertips? Better yet, what if you could have a conversation with it to curate, shape, and generate content for your team—all with AI's help?

This was prime territory for building my first MCP server: a hockey knowledge base. But not just another API wrapped around a database. MCP servers are designed specifically for how LLMs work—they anticipate what context is needed, understand the kinds of questions that will be asked, and provide deep domain expertise. It's an API shaped for AI, not systems.

I didn't create this content—I liberated it. Using Claude Code, I parsed public coaching PDFs, scraped websites, and indexed YouTube videos. The result: 1,200+ drills, 150+ skill progressions, 90 practice themes, 40+ tactical systems, and hundreds of coaching videos—all properly attributed and enriched with metadata like age levels and complexity ratings.

The Hockey-KB MCP server provides tools like `search_drills`, `search_tactics`, `search_videos`, and `get_skill_progressions`. Now when I need a practice plan, I can ask: "Find passing drills for U10 that work on timing" or "What defensive systems work for kids just learning positioning?" The MCP understands context—it knows U10 means simpler setups, that "timing" implies give-and-go patterns, that defensive systems for beginners need to be zone-based, not man-to-man.

Best part? This works anywhere that supports MCP—Claude Desktop (shown in the video), Claude Code, ChatGPT, Gemini, VS Code, or your own custom app. Build once, use everywhere.

**Watch it in action:**

*This 70-second demo shows natural language searches finding exactly what I need: passing drills for give-and-go plays, defensive zone systems appropriate for 9-year-olds, and even relevant YouTube videos. Notice how it filters for age-appropriate complexity without being asked.*

[Video: Claude Desktop using Hockey-KB MCP to find drills and systems]

## From Whiteboard to Digital

Every coach knows the ritual—standing at the rink whiteboard, drawing X's and O's, arrows everywhere. The problem? That diagram dies when practice ends. I wanted a library of digital diagrams I could reuse, share with kids so they could study before practice, or let them work through on their own time.

This turned out to be the hardest technical challenge. Ask AI to "draw a 2-1-2 forecheck" and you'll get abstract art, ASCII nonsense, or beautiful illustrations that look nothing like coaching diagrams. 

[Image: AI-generated "protect the house" formation - artistic but useless for coaching]

It took dozens of iterations to crack this. The breakthrough was realizing AI shouldn't draw—it should translate. Here's what happens under the hood:

**User prompt:** "Show protecting the house defensive coverage"
**AI translates:** "Two defensemen in front of net, one forward covering slot"
**MCP generates spec:**
```json
{
  "players": [
    {"id": "D1", "x": 45, "y": 25, "team": "home"},
    {"id": "D2", "x": 55, "y": 25, "team": "home"},
    {"id": "F1", "x": 50, "y": 35, "team": "home"}
  ],
  "zones": [{"type": "coverage", "area": "house"}]
}
```
**Result:** Precise PNG diagram with players in exact positions

It's separation of concerns: AI handles hockey concepts, code handles spatial precision.

**Watch the reality of building with AI tools:**

*This demo shows what actually happens—it's not perfect on the first try. Watch Claude and the Hockey Diagram MCP work through iterations to create a defensive zone coverage diagram. Yes, there's some "AI dancing" as we figure out the right prompts. The final result? A professional PNG uploaded to Cloudinary, ready to share.*

[Video: Claude Desktop generating hockey diagram with iterations]

Is it faster than drawing on a whiteboard? No—that takes 30 seconds. But now I have a growing library of diagrams, kids can review them before practice on their phones, and I can generate variations instantly. The same pattern applies to any domain needing spatial precision—network diagrams, floor plans, process flows. Human concepts need translation to precise specifications.

## Tracking What Actually Works

Most volunteer coaches track nothing, use a notebook that gets coffee-stained, or maintain a spreadsheet that becomes chaos by November. I was in the notebook camp—scribbling notes between drills, never looking at them again. Meanwhile, I kept running the same drills that didn't work, forgetting which ones clicked with the kids.

Enter Airtable with the MCP integration. Now tracking isn't a chore—it's a conversation. After practice, I tell Claude what happened and it updates everything. Which drills worked (that 2v2 battle drill? "Great"). Which ones didn't (the 3v3? "Fix it"—kids weren't ready). Who's struggling with what concepts. What to try next time.

Here's the magic—using the Airtable MCP in Claude Code:

```bash
$ claude "The 3v3 defensive drill was too complex. Kids kept collapsing to net."

Claude: Updating October 31st practice notes...
✓ 3v3 Small Area Game: "Fix it" (was chaos)
✓ Added note: "Kids not ready for 3v3 complexity - all collapsed to net 
  instead of staying with their check. Back to 2v2 foundation needed."
✓ Tagged skills to revisit: [positioning, defensive_awareness]

Based on your data, your 2v2 drills are rated "Great" consistently. 
Want me to find similar 2v2 progressions for next practice?
```

Now when planning next practice, I ask "What defensive drills have worked best?" and get actual data, not vague memories. Same approach works for game stats—remember that game recap automation from the Claude Code video? Turn raw stats into stories for kids and parents, or into tactical analysis for coaches. Evidence-based coaching instead of hoping I remember what worked.

## Beyond Ice Time Learning

We get 2-3 hours of ice time per week. That's it. Meanwhile, kids need to understand defensive zone coverage, forechecking patterns, breakout plays—complex concepts that take repetition to stick. Telling them once at practice doesn't cut it.

I built two things with the goal of helping kids become students of the game in a fun, engaging way. First, a Notion team site (Notion is like Google Docs meets a database—perfect for building interactive team wikis) that's our living playbook—embedded videos, diagrams, systems explained in Grade 4 language. Second, a quiz app designed to turn learning into competition (nothing should motivate 9-year-olds more than beating their friends on a leaderboard).

The quiz design is what I'm most excited about. It doesn't just mark answers wrong—it teaches through Socratic questioning:

```
Question: "In a 2-1-2 forecheck, where should F3 position themselves?"
Kid answers: "In front of the net"

AI Coach: "Good thinking about net coverage! 🏒 
But let's think about this together:
If F1 and F2 are down low...
Who's watching the middle of the ice?"

Kid's second attempt: "Oh! High slot!"

AI Coach: "EXACTLY! 🎯 You're now #3 on the leaderboard!"
```

Built with Claude Code in one evening—Next.js frontend, OpenAI for hints, scores syncing to our Notion database. Just released it to the team, so we'll see how it goes. The vision is kids learning systems through play, competing with friends, maybe even quizzing each other off-ice.

**See our digital playbook in action:**

*This video tours our team's new Notion site—the playbook we're rolling out, the quiz app ready for kids to try, and Claude Desktop with Notion MCP updating practice plans in real-time. Watch a demo of the quiz flow, explore the playbook, and see how everything connects.*

[Video: Notion team site tour with quiz app and Claude updates]

## Connecting the Dots with n8n

We use TeamSnap for scheduling—it's what every hockey team knows. But I wanted our Notion playbook to show the schedule too, enhanced with context parents actually need. Manual copy-paste? Not happening.

Enter n8n—visual workflow automation. Like IFTTT or Zapier, it connects different services, but n8n gives you complete control with a visual programming interface. You see your entire automation as a flowchart, each node doing one thing, data flowing through like a pipeline you can inspect at every step.

![n8n Workflow: TeamSnap → AI → Notion](images/n8n_workflow.png)

My morning workflow: TeamSnap API → Transform dates/times → OpenAI (adds "Early game! Pack snacks!" context) → Notion update. Built it using Claude Code with the n8n MCP tool—told Claude what I wanted, it generated the workflow JSON, deployed it. Reality check: n8n is powerful but finicky. Getting all the nodes configured correctly, authentication working, data transformations right—it takes patience and debugging.

Worth it though. Now when games get rescheduled, parents see updates instantly with helpful context. Next up: building a similar workflow to generate weekly team emails—pull the schedule, add personalized reminders, format it nicely, ready to send. No more "what time should we arrive?" texts. The pattern works for any system integration—CRM to Slack, Jira to Teams, anywhere data needs enhancement before reaching its destination.

## The Failures That Taught Me Everything

Nothing worked perfectly the first time. The MCP server crashed constantly until I figured out connection pooling. The diagram generator produced abstract art. The n8n workflow took 63 minutes of debugging to work.

Here's my biggest reflection: There's no substitute for rolling up your sleeves and just starting. The videos show real development—iterations, debugging, figuring it out. That's the reality of building with AI.

Claude Code made iteration fast. Fail, fix, try again—all in one evening instead of weeks. Building with AI is different. It's not traditional programming where you control every line. It's collaboration with a system that sometimes surprises you—both good and bad.

## Looking Back: What Actually Works

After months of building, here's what I've learned about working with AI:

**AI as assistant, not automation.** The temptation is to "automate everything" but that's not where AI shines. It's best as a skilled assistant—you drive, it accelerates. The human-led, AI-assisted model consistently beats pure automation.

**Play to its strengths and power it up.** LLMs alone are powerful but limited. Add MCP tools and they become transformative. Hockey knowledge + Claude = helpful. Hockey MCP + Claude = practice plans in seconds. The tools multiply the capability.

**Iterations and evaluation build confidence.** That diagram tool? Took dozens of attempts. But once it worked, I could trust it. The key is building in feedback loops—test, evaluate, adjust. Never assume the first output is right.

**The MCP explosion needs governance.** MCP servers are flooding in—everyone's building them. But security and governance around these open-source tools need sorting before enterprise adoption. Who's vetting these? What data are they accessing? Solutions like MCP registries are coming, but we're in the wild west phase.

## Beyond Hockey: The Pattern Applies Everywhere

These patterns extend to every domain I'm passionate about:

**Government:** Citizen inquiries trapped in call center scripts? Build an MCP for policy knowledge. Permit applications requiring manual review? AI can pre-screen and flag issues. The same knowledge liberation pattern applies to public service delivery.

**Healthcare:** Treatment protocols in dense medical journals? Searchable, contextual MCP. Patient education materials at Grade 12 reading level? AI translation to appropriate levels. Care coordination between systems? n8n-style visual workflows.

**Project/App Delivery:** Requirements scattered across Confluence pages? Knowledge MCP. Architecture decisions in Slack threads? Captured and searchable. Sprint retrospectives that actually drive improvement? Data-driven insights from tracked patterns.

The problems are universal: trapped knowledge, complex translations, disconnected systems, engagement challenges. The solutions follow the same patterns.

## Your Turn to Build

The gap between idea and implementation has never been smaller. These tools took evenings and weekends, not months and budgets.

**Want to try these tools yourself?**
- Claude Code is free to start
- MCP servers are open source
- n8n has a generous free tier
- The hockey tools are on GitHub (search "thunder_playbook")

**Have a similar challenge to solve?**
Reach out. I'd love to hear what patterns you see in your world, what problems keep you up at night, what tools could give you back time to focus on what matters. Whether it's coaching, government services, healthcare delivery, or building better software—the patterns are there.

Because in the end, it's not about the technology. It's about having more time for what matters—whether that's teaching kids to love hockey, serving citizens better, or shipping products that delight users.

The future isn't AI replacing humans. It's humans with AI tools doing what they do best, just better.