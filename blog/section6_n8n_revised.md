## Problem #5: The Automation Bridge

We use TeamSnap for scheduling—it's what everyone knows, and it works. But I wanted our Notion team site to show the schedule too, always in sync, without me copying and pasting every change.

Enter n8n—a workflow automation platform that's like having a visual programming language for connecting services. If you haven't used it, imagine being able to see your entire automation as a flowchart, with each step (called a "node") doing one specific thing. You can inspect data at every step, debug visually, and modify by dragging and dropping new nodes.

Here's the workflow I built to keep our schedule synchronized:

*[SCREENSHOT PLACEHOLDER: n8n workflow canvas showing the complete TeamSnap to Notion pipeline]*

**The Pipeline:**

**Step 1: Schedule Trigger**
Every morning at 5 AM, the workflow wakes up. Simple cron job, but visual—I can see when it last ran, when it's running next.

**Step 2: Fetch from TeamSnap**
Connect to TeamSnap's API and pull the next 14 days of events. The raw data is messy—dates in ISO format, separate fields for game time vs arrival time, location data nested three levels deep.

**Step 3: Data Transformation**
Clean up the chaos. Convert dates to readable format ("Nov 15" not "2024-11-15T00:00:00Z"). Determine if it's a game or practice. Extract the actual location name. Make it human-readable.

**Step 4: AI Enhancement**
This is where it gets interesting. Feed each event to OpenAI with context:
- "This is a tournament game at 8 AM"
- AI adds: "Early game! Pack snacks and arrive by 7:15 AM for warm-up. Both jerseys required."

The AI understands hockey parent needs—what gear to bring, when to arrive, what to prepare.

**Step 5: Push to Notion**
Update our team database with the enhanced schedule. Each event now has helpful context, not just raw times and dates.

*[VIDEO PLACEHOLDER: Workflow execution showing data transformation at each node]*

**Why n8n Changes Everything:**

1. **Visual, Not Buried in Code**
   I can see the entire pipeline. When something breaks (TeamSnap changed their API last month), I can see exactly which node failed and why.

2. **Node-by-Node Inspection**
   Click any node, see the exact data going in and coming out. No console.log debugging—it's all right there.

3. **Drag-and-Drop Evolution**
   Want to add Slack notifications? Drag in a Slack node. Want to filter out optional practices? Add a filter node. No coding required.

4. **Built from Claude Code**
   Here's the kicker—I built this entire workflow using Claude Code. Described what I wanted, Claude helped create the JSON workflow definition, deployed it to n8n. Any MCP-enabled client could do the same.

```bash
$ claude "Create an n8n workflow that syncs TeamSnap schedule to Notion"

Claude: I'll help you build that workflow. Let me create the JSON definition
with the nodes you need...

[Creates complete workflow definition]
[Deploys to n8n instance]
[Tests with sample data]

Workflow deployed and running! It will sync every morning at 5 AM.
Want to add email notifications when games change?
```

**What's Next:**

I'm already building new pipelines:

**Practice Plans Pipeline:**
Notion (new practice plan) → AI (format for parents) → Gmail & WhatsApp

**Game Recap Pipeline:**
Airtable (game stats) + Coach notes → AI (write summary) → Team email

**Tournament Logistics:**
Multiple TeamSnap events → AI (create day plan) → Notion itinerary

*[DIAGRAM PLACEHOLDER: Future workflow possibilities]*

**This Pattern Is Everywhere**

Every organization has this same challenge—data in one system, needs to be in another, but better.

**Sales & Marketing:**
- CRM → AI enhancement → Customer portal
- Lead forms → AI qualification → Sales team notifications
- Campaign results → AI analysis → Executive dashboards

**HR & Operations:**
- Applicant tracking → AI screening → Hiring manager summaries
- Time tracking → AI patterns → Resource planning
- Employee feedback → AI themes → Action items

**IT & Development:**
- GitHub issues → AI prioritization → Sprint planning
- System alerts → AI diagnosis → Incident tickets
- Deploy logs → AI summary → Stakeholder updates

The pattern: Source system → AI enrichment → Destination system. All visible, all debuggable, all modifiable without touching code.

*For my enterprise friends: How many of your integrations are black boxes? How many require developers to modify? n8n puts the power back in your hands.*