## Problem #5: The Learning Gap

We work on systems and plays at practice, but there's only so much ice time. Kids need to understand the why behind what we're teaching, not just follow directions. I wanted them to be students of the game.

The content exists—tons of it. YouTube channels breaking down forechecks. Websites explaining defensive positioning. PDFs with skill progressions. Nothing that hasn't been covered before. But it's scattered everywhere, and no nine-year-old (or their parent) has time to search through it all.

I needed a place to house curated, kid-friendly hockey knowledge. Not another PDF. Not emails. Something they'd actually use.

Then I discovered Notion.

If you haven't used Notion, imagine if Google Docs, Wikipedia, and a database had a baby—and that baby was actually beautiful. It's a workspace that feels like building a website without writing any code. You create pages using "blocks"—text, images, videos, databases, embeds—that snap together like Lego. Rich formatting, multiple views, linked databases, all with a URL you can share.

**Building Our Team's Digital Playbook**

Using Claude Code and the Notion MCP tool, I built our team site in an afternoon:

```bash
$ claude "Let's build a hockey team site in Notion for U10 players to learn systems"

Claude: I'll help you create a comprehensive team site. Looking at your 
Notion workspace...

Let me create the structure:
✓ Main team page with sections for goals and team identity
✓ Thunder Systems database for plays and formations  
✓ Thunder Drills database linked to practice plans
✓ Thunder Code (team rules and values)
✓ Schedule integration ready for n8n
✓ Quiz leaderboard to track learning

Building the playbook now...
```

*[SCREENSHOT PLACEHOLDER: Team homepage showing "Thunder Way" and season goals]*

Here's what our actual site became:

**Homepage: Team Identity**
```
🎯 2025-2026 SEASON GOALS
🏆 OUR TARGETS:
- Win more faceoffs than we lose
- Score first in 70% of games
- Allow less than 3 goals per game

⚡ THE THUNDER WAY
💥 OUR PROMISE: "We bring the storm every shift, every game!"
```

**The Playbook That Teaches**

The Thunder Systems section isn't just diagrams—it's multimedia learning:

```
📚 DEFENSIVE ZONE COVERAGE - BOX+1
[Embedded YouTube video: "NHL Teams Running Box+1"]
[AI-generated diagram showing positions]

"Hey Thunder players! 🏒 Box+1 is like playing 
tag but in reverse - everyone has someone to 
watch, and one player (that's the +1) chases 
the puck. Think of it like this..."

[Kid-friendly explanation in grade 4 language]

WHEN WE USE IT: Against teams that like to 
pass a lot behind our net

WATCH FOR: Don't all chase the puck! 
Stay with your check!
```

*[VIDEO PLACEHOLDER: Scrolling through the playbook showing embedded videos and diagrams]*

**How It Came Together**

Building this wasn't manual content creation. It was AI-powered curation:

1. **Video Discovery**: Used YouTube MCP to find relevant coaching videos
```bash
$ claude "Find videos explaining box+1 defensive coverage for kids"

Claude: Searching YouTube for educational hockey content...
Found: "Hockey Canada: Defensive Zone Systems" (timestamp 3:42)
This segment clearly shows box+1 with youth players. 
Embedding at the specific timestamp...
```

2. **Visual Learning**: Generated diagrams and had ChatGPT create kid-friendly hockey illustrations

3. **Grade-Appropriate Content**: Every explanation written for Grade 4 reading level
```bash
$ claude "Explain the neutral zone trap for 9-year-olds"

Claude: Writing in kid-friendly language...

"The neutral zone trap is like setting up a wall at center 
ice! Instead of chasing the other team all over, we wait 
for them to come to us. When they try to skate through 
center ice - SURPRISE! - we're all there waiting!"
```

**The Real Value**

Not everyone will use it—some kids just want to play, and that's perfect. But for those who want to learn, it's there. For parents who want to help their kids understand the game, it's there. And next season? Just update it with new systems, new videos, new learning. The foundation is built.

*[SCREENSHOT PLACEHOLDER: Kid viewing the site on iPad, watching embedded drill video]*

**This Changes Everything for Training Content**

This pattern revolutionized how I think about documentation:

```bash
$ claude "Use Playwright to document our quiz app for training"

Claude: I'll use Playwright MCP to automatically capture your app...

Opening app...
✓ Screenshot: Login screen
✓ Screenshot: Main quiz interface
✓ Screenshot: Hint system in action
✓ Screenshot: Leaderboard view

Creating Notion training page...
✓ Embedding screenshots in logical flow
✓ Adding annotations and callouts
✓ Creating interactive walkthrough

Training documentation created in 5 minutes!
```

Instead of hours manually screenshotting and annotating, Playwright MCP automatically:
- Opens your app
- Navigates through workflows
- Captures screenshots at key points
- Injects them directly into Notion pages

*[VIDEO PLACEHOLDER: Playwright automatically documenting an app and creating Notion guide]*

**Where This Pattern Applies**

**Software Training**
- Automated screenshot capture of your app
- Step-by-step guides with real UI images
- Version-controlled documentation that updates with your app

**Employee Onboarding**
- Curated knowledge from scattered resources
- Role-specific learning paths
- Embedded training videos at point of need

**Product Documentation**
- User guides built from actual product interaction
- FAQ sections powered by support ticket analysis
- Video tutorials embedded at point of need

**Educational Content**
- Curated learning from multiple sources
- Grade-appropriate explanations
- Mixed media (video, images, text) for different learning styles

The pattern: Scattered knowledge → AI curation → Beautiful, accessible hub.

*For my business friends: How much time do you spend creating training materials? How often are they out of date by the time you publish? This changes that equation.*