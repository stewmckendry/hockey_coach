# Video Demo Scripts for Blog Post

## Demo 1: Claude Code with MCP Tools (90 seconds)
**Location:** Warp Terminal with Claude Code
**Purpose:** Show the power of Claude + MCP tools for rapid development

### Script (with timing):

**0:00-0:10** - Opening shot
```bash
$ claude "Build a shot tracking feature for our hockey app using 
Airtable for storage and Playwright for testing"
```

**0:10-0:20** - Plan Mode (show briefly, then fast-forward)
```
Claude: Creating development plan...
[Show plan mode briefly]
✓ GitHub Issue #127 created
✓ Feature branch created
✓ Architecture defined
```

**0:20-0:35** - MCP Tools in Action (key highlight)
```
Claude: Using MCP tools to set up infrastructure...

[Airtable MCP] Creating Shot_Tracking table...
✓ Table created with 6 fields

[Hockey-KB MCP] Finding best practices for shot metrics...
✓ Found NHL analytics patterns

[Fast-forward through actual queries]
```

**0:35-0:50** - Parallel Development (speed up 4x)
```
Launching parallel agents:
- Agent 1: Building API layer
- Agent 2: Creating React components  
- Agent 3: Writing Playwright tests

[Show split screen with files being created rapidly]
[Speed up 4x with counter showing "12 files created"]
```

**0:50-0:70** - Playwright Testing (real-time highlight)
```
Claude: Running automated UI tests...

[Show browser opening automatically]
[Tests running through the app]
✓ All 8 E2E tests passing
✓ 100% code coverage
```

**0:70-0:85** - Final Result
```
COMPLETE: Shot tracking feature ready
- GitHub PR created
- Tests passing
- Deployed to staging
- Time elapsed: 18 minutes
```

**0:85-0:90** - Closing
Show live app with shot tracking working

### Key Moments:
- MCP tools working together (Airtable, Hockey-KB, Playwright)
- Parallel agents developing simultaneously 
- Automated testing with Playwright
- 18 minutes from idea to deployed feature

---

## Demo 2: Knowledge Base Search (90 seconds)
**Note:** Will be done in Claude Desktop for better UI
**Location:** Terminal running hockey_mcp

### Script:
1. Show natural language query:
   ```
   "passing drills for U10 give-and-go neutral zone"
   ```
2. Display returned results with structure
3. Show different query:
   ```
   "What defensive systems work for 9-year-olds?"
   ```
4. Show comprehensive results with teaching points
5. Quick montage of various searches

### Key Points:
- Instant access to 1000+ drills
- Natural language understanding
- Structured, useful results

---

## Demo 3: Diagram Generation Workflow (2 minutes)
**Note:** Will be done in Claude Desktop for better UI
**Location:** Split screen - Terminal and SVG output

### Script:
1. Type drill description:
   ```
   "2-1-2 forecheck with F1 behind net, F2 strong side, F3 high slot"
   ```
2. Show MCP processing steps:
   - Analysis phase
   - Coordinate mapping
   - Validation
3. Display generated SVG diagram
4. Make adjustment: "Move F3 to weak side high"
5. Show instant diagram update
6. Export to practice plan PDF

### Key Points:
- Natural language to precise diagrams
- Real-time adjustments
- Professional output quality

---

## Demo 4: Airtable Practice Planning (90 seconds)
**Location:** Airtable interface

### Script:
1. Show Practice Planning view
2. Create new practice:
   - Select date/time
   - Choose theme: "Defensive Zone Coverage"
   - Link drills from library (drag and drop)
3. Show automatic duration calculation
4. Display Player Development view:
   - Filter: "Skills needing work"
   - Show Liam's progression chart
5. Mobile view for practice check-in

### Key Points:
- Visual database management
- Linked relationships
- Mobile accessibility

---

## Demo 5: n8n Workflow Execution (2 minutes)
**Location:** n8n browser interface

### Script:
1. Show complete workflow canvas
2. Trigger manual execution
3. Follow data through each node:
   - TeamSnap API call (show raw data)
   - Data transformation (show cleaned data)
   - OpenAI enrichment (show added context)
   - Notion update (show result)
4. Show execution history
5. Display Notion page with updated schedule

### Key Points:
- Visual workflow building
- Step-by-step debugging
- AI as workflow node
- Automatic synchronization

---

## Demo 6: Quiz App with AI Hints (90 seconds)
**Location:** Web browser with quiz app

### Script:
1. Login as "Tommy" (demo account)
2. Start quiz question about forechecking
3. Submit wrong answer intentionally
4. Show AI's Socratic hint (not answer)
5. Submit improved answer
6. Show celebration and points
7. Display leaderboard update
8. Show coach dashboard with comprehension stats

### Key Points:
- Age-appropriate interaction
- Learning through questions
- Gamification elements
- Progress tracking

---

## Demo 7: Full Integration Flow (3 minutes)
**Location:** Multiple windows showing system working together

### Script:
1. Start with coaching scenario: "Plan tomorrow's practice"
2. Search knowledge base for drills
3. Generate diagrams for selected drills
4. Add to Airtable practice plan
5. Show n8n workflow publishing to Notion
6. Preview parent-facing team page
7. Show quiz questions auto-generated from practice focus
8. Display all components working as ecosystem

### Key Points:
- Seamless integration
- Time savings illustrated
- Multiple stakeholders served
- Single source of truth

---

## Essential Screenshots & Images (10 Key Visuals)

### Must-Have Images:

1. **n8n Workflow Canvas** (CRITICAL)
   - Full TeamSnap → OpenAI → Notion workflow
   - Show all nodes connected with data flow
   - Include one close-up of AI enhancement node

2. **Claude Code with MCP Tools**
   - Warp terminal showing MCP tools in action
   - Split view: command and response
   - Show "✓ Tests passing" prominently

3. **Hockey Diagram Comparison**
   - Side-by-side: Whiteboard sketch vs Clean SVG
   - Same play in both formats
   - Shows transformation quality

4. **Airtable Practice Dashboard**
   - Calendar view with drill success rates
   - Clean, data-rich interface
   - Mobile view in corner

5. **Notion Team Playbook**
   - Homepage with embedded videos/diagrams
   - Show quiz leaderboard integration
   - Kid-friendly design

6. **Quiz App in Action**
   - Question with Socratic hint visible
   - Leaderboard showing engagement
   - Clean, playful UI

7. **Before/After Time Comparison**
   - Simple graphic: "3 hours → 20 minutes"
   - Show task: "Create practice plan with diagrams"

8. **System Architecture**
   - Clean diagram showing all tools connected
   - MCP at the center
   - Data flow arrows

9. **Playwright Testing**
   - Browser automating test
   - Green checkmarks for passed tests
   - "100% Coverage" badge

10. **Mobile Experience**
    - Phone showing Notion site
    - Parent-friendly schedule view
    - Professional but accessible